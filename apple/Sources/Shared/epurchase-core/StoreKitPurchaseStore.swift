import Foundation
import Observation
import StoreKit

/// StoreKit 的购买结果。待批准和取消都不授予权益。
public enum StoreKitPurchaseOutcome: Sendable, Equatable {
    case purchased
    case cancelled
    case pending
}

/// 管理非消耗型商品和自动续订商品。应用持有一个实例，并按实际权益决定功能访问。
@MainActor
@Observable
public final class StoreKitPurchaseStore {
    /// 已加载且类型受支持的商品，价格使用 StoreKit 的本地化值。
    public private(set) var products: [Product] = []
    public private(set) var productLoadError: String?
    /// 权益扫描失败时保留已确认快照，并将错误提供给宿主。
    public private(set) var entitlementError: String?
    public private(set) var isPurchasing = false
    public private(set) var isRestoring = false
    public private(set) var hasLoadedEntitlements = false
    public var isLoadingProducts: Bool { productLoad != nil }

    /// 当前有效商品。首轮读取完成前可通过 hasLoadedEntitlements 区分未知与未购。
    public var purchasedProductIDs: Set<String> {
        let now = Date()
        return Set(entitlements.compactMap { id, entry in entry.access.isActive(at: now) ? id : nil })
    }

    /// 当前已确认的最长有效订阅期限，含 StoreKit 已验签的宽限期。
    public var subscriptionExpirationDate: Date? {
        let now = Date()
        return entitlements.values.compactMap { $0.access.expirationDate }.filter { $0 > now }.max()
    }

    private let productIDs: Set<String>
    private let supportedTypes: Set<Product.ProductType>
    private let expectedTypes: [String: Product.ProductType]
    private var entitlements: [String: Entry] = [:]
    private var productLoad: Task<Void, Never>?
    @ObservationIgnored private var entitlementLoad: Task<Void, any Error>?
    @ObservationIgnored private var updates: Task<Void, Never>?
    @ObservationIgnored private var subscriptionUpdates: Task<Void, Never>?
    @ObservationIgnored private var expiration: Task<Void, Never>?
    @ObservationIgnored private var entitlementGeneration = 0
    @ObservationIgnored private var recentTransactions: [String: Transaction] = [:]
    @ObservationIgnored var onEntitlementChange: (@MainActor (StoreKitPurchaseStore) -> Void)?

    private struct Entry {
        let transaction: Transaction
        let access: StoreKitPurchaseEntitlement
    }

    /// 使用 App Store Connect 或 StoreKit 测试配置中的商品 ID。月付、年付和买断可一起配置。
    public convenience init(productIDs: [String]) {
        self.init(productIDs: productIDs, supportedTypes: [.nonConsumable, .autoRenewable])
    }

    /// 约束每个 ID 的商品类型。可将成功应用的权益快照同步给宿主的其他进程。
    public convenience init(
        productTypes: [String: Product.ProductType],
        onEntitlementChange: (@MainActor (StoreKitPurchaseStore) -> Void)? = nil
    ) {
        self.init(
            productIDs: Array(productTypes.keys),
            supportedTypes: Set(productTypes.values).intersection([.nonConsumable, .autoRenewable]),
            expectedTypes: productTypes
        )
        self.onEntitlementChange = onEntitlementChange
    }

    init(productIDs: [String], supportedTypes: Set<Product.ProductType>, expectedTypes: [String: Product.ProductType] = [:]) {
        self.productIDs = Set(productIDs)
        self.supportedTypes = supportedTypes
        self.expectedTypes = expectedTypes
    }

    deinit {
        updates?.cancel()
        subscriptionUpdates?.cancel()
        expiration?.cancel()
    }

    /// 应用启动调用。幂等地监听后续交易，同时加载商品和当前权益。
    public func startIfNeeded() {
        guard updates == nil else { return }
        startListening()
        Task { [weak self] in await self?.reloadProducts() }
    }

    /// 更新商品价格和权益。商品读取失败写入 productLoadError 供界面展示。
    public func reloadProducts() async {
        startListening()
        async let load: Void = loadProducts()
        // 权益失败由 entitlementError 保留，仍完成商品价格读取。
        try? await refreshEntitlements()
        await load
    }

    /// 刷新当前权益，适用于 App 回到前台或需要再次确认功能授权时。
    public func refreshEntitlements() async throws {
        startListening()
        if let entitlementLoad {
            try await entitlementLoad.value
            return
        }
        let task = Task<Void, any Error> { [weak self] in try await self?.scanEntitlements() }
        entitlementLoad = task
        try await task.value
    }

    /// 购买配置中的商品。已持有对应权益时直接返回购买成功，避免重复触发系统付款。
    public func purchase(_ productID: String) async throws -> StoreKitPurchaseOutcome {
        guard productIDs.contains(productID) else { throw StoreError.productUnavailable }
        guard !isPurchasing, !isRestoring else { throw OperationError.inProgress }
        isPurchasing = true
        defer { isPurchasing = false }
        try await refreshEntitlements()
        if purchasedProductIDs.contains(productID) { return .purchased }
        if !products.contains(where: { $0.id == productID }) { await loadProducts() }
        guard let product = products.first(where: { $0.id == productID }) else { throw StoreError.productUnavailable }

        switch try await product.purchase() {
        case let .success(.verified(transaction)):
            guard transaction.productID == productID, supports(transaction),
                  let entry = try await currentEntry(for: transaction)
            else { throw OperationError.inactiveEntitlement }
            record(transaction, entry: entry)
            await transaction.finish()
            guard purchasedProductIDs.contains(productID) else { throw OperationError.inactiveEntitlement }
            return .purchased
        case .success(.unverified):
            throw StoreError.unverified
        case .userCancelled:
            return .cancelled
        case .pending:
            return .pending
        @unknown default:
            throw StoreError.unverified
        }
    }

    /// 用户明确发起恢复时同步 App Store，随后刷新已验证权益。
    public func restore() async throws {
        guard !isPurchasing, !isRestoring else { throw OperationError.inProgress }
        isRestoring = true
        defer { isRestoring = false }
        startListening()
        try await AppStore.sync()
        entitlementGeneration &+= 1
        try await refreshEntitlements()
    }

    private func startListening() {
        guard updates == nil else { return }
        updates = Task { [weak self] in
            for await result in Transaction.updates {
                guard let self else { return }
                switch result {
                case let .verified(transaction) where self.supports(transaction):
                    self.record(transaction, entry: self.entry(for: transaction))
                    try? await self.refreshEntitlements()
                    await transaction.finish()
                case let .unverified(transaction, _) where self.productIDs.contains(transaction.productID):
                    self.entitlementError = StoreError.unverified.localizedDescription
                default:
                    break
                }
            }
        }
        guard supportedTypes.contains(.autoRenewable) else { return }
        subscriptionUpdates = Task { [weak self] in
            for await _ in Product.SubscriptionInfo.Status.updates {
                guard let self else { return }
                // 宽限期变化可能没有新交易，旧快照必须重新读取。
                self.entitlementGeneration &+= 1
                try? await self.refreshEntitlements()
            }
        }
    }

    func loadProducts() async {
        if let productLoad {
            await productLoad.value
            return
        }
        let task = Task<Void, Never> { [weak self] in
            guard let self else { return }
            defer { self.productLoad = nil }
            do {
                self.products = try await Product.products(for: self.productIDs)
                    .filter { self.supports(productID: $0.id, type: $0.type) }
                self.productLoadError = self.products.isEmpty ? StoreError.productUnavailable.localizedDescription : nil
            } catch {
                self.products = []
                self.productLoadError = error.localizedDescription
            }
        }
        productLoad = task
        await task.value
    }

    private func supports(_ transaction: Transaction) -> Bool {
        supports(productID: transaction.productID, type: transaction.productType)
    }

    private func supports(productID: String, type: Product.ProductType) -> Bool {
        productIDs.contains(productID) && supportedTypes.contains(type) &&
            (expectedTypes[productID].map { $0 == type } ?? true)
    }

    private func record(_ transaction: Transaction, entry: Entry?) {
        let id = transaction.productID
        let newest = recentTransactions[id] ?? entitlements[id]?.transaction
        if let newest, newest.purchaseDate > transaction.purchaseDate { return }
        entitlementGeneration &+= 1
        // StoreKit 的当前权益序列可能稍晚才收录刚在本机交付的交易。
        recentTransactions[id] = transaction
        if let entry {
            entitlements[id] = entry
        } else if transaction.revocationDate != nil || transaction.isUpgraded {
            entitlements.removeValue(forKey: id)
        }
        publishEntitlements()
    }

    private func scanEntitlements() async throws {
        defer { entitlementLoad = nil }
        repeat {
            let generation = entitlementGeneration
            do {
                let (next, confirmed) = try await readEntitlements(pending: recentTransactions)
                // 扫描挂起期间若有购买或恢复，重读以防旧快照覆盖新交易。
                guard generation == entitlementGeneration else { continue }
                for id in confirmed { recentTransactions.removeValue(forKey: id) }
                entitlements = next
                hasLoadedEntitlements = true
                entitlementError = nil
                publishEntitlements()
                return
            } catch {
                guard generation == entitlementGeneration else { continue }
                entitlementError = error.localizedDescription
                throw error
            }
        } while !Task.isCancelled
    }

    private func readEntitlements(pending: [String: Transaction]) async throws -> ([String: Entry], Set<String>) {
        var next: [String: Entry] = [:]
        var confirmed = Set<String>()
        for await result in Transaction.currentEntitlements {
            guard let transaction = try verifiedTransaction(result) else { continue }
            let id = transaction.productID
            if let recent = pending[id] {
                guard transaction.id == recent.id || transaction.purchaseDate > recent.purchaseDate else { continue }
                confirmed.insert(id)
                if transaction.id == recent.id, recent.revocationDate != nil || recent.isUpgraded { continue }
            }
            next[id] = try await currentEntry(for: transaction)
        }
        for (id, transaction) in pending where !confirmed.contains(id) {
            if case let .verified(latest)? = await Transaction.latest(for: id),
               latest.purchaseDate > transaction.purchaseDate ||
               (latest.id == transaction.id && (latest.revocationDate != nil || latest.isUpgraded)) {
                confirmed.insert(id)
            } else if let entry = entry(for: transaction) {
                next[id] = entry
            }
        }
        return (next, confirmed)
    }

    private func verifiedTransaction(_ result: VerificationResult<Transaction>) throws -> Transaction? {
        switch result {
        case let .verified(transaction):
            return supports(transaction) ? transaction : nil
        case let .unverified(transaction, _):
            if productIDs.contains(transaction.productID) { throw StoreError.unverified }
            return nil
        }
    }

    private func entry(for transaction: Transaction, grace: Date? = nil) -> Entry? {
        StoreKitPurchaseEntitlement.resolve(
            productType: transaction.productType,
            expirationDate: transaction.expirationDate,
            revocationDate: transaction.revocationDate,
            isUpgraded: transaction.isUpgraded,
            gracePeriodExpirationDate: grace,
            now: Date()
        ).map { Entry(transaction: transaction, access: $0) }
    }

    private func currentEntry(for transaction: Transaction) async throws -> Entry? {
        if let result = entry(for: transaction) { return result }
        guard transaction.productType == .autoRenewable,
              transaction.revocationDate == nil, !transaction.isUpgraded,
              let groupID = transaction.subscriptionGroupID
        else { return nil }
        var grace: Date?
        for status in try await Product.SubscriptionInfo.status(for: groupID) where status.state == .inGracePeriod {
            guard let current = try verifiedTransaction(status.transaction), current.productID == transaction.productID,
                  current.originalID == transaction.originalID, current.revocationDate == nil, !current.isUpgraded
            else { continue }
            guard case let .verified(renewal) = status.renewalInfo else { throw StoreError.unverified }
            if let end = renewal.gracePeriodExpirationDate, grace.map({ end > $0 }) ?? true { grace = end }
        }
        return entry(for: transaction, grace: grace)
    }

    private func publishEntitlements() {
        expiration?.cancel()
        if let deadline = entitlements.values.compactMap({ $0.access.expirationDate }).min() {
            let delay = max(0, deadline.timeIntervalSinceNow)
            expiration = Task { [weak self] in
                do { try await Task.sleep(for: .seconds(delay)) }
                catch { return }
                try? await self?.refreshEntitlements()
            }
        }
        onEntitlementChange?(self)
    }

    private enum OperationError: LocalizedError {
        case inProgress
        case inactiveEntitlement

        var errorDescription: String? {
            switch self {
            case .inProgress: String(localized: "A purchase or restore is already in progress.")
            case .inactiveEntitlement: String(localized: "The App Store hasn’t confirmed access to this purchase.")
            }
        }
    }
}

enum StoreKitPurchaseEntitlement: Equatable {
    case lifetime
    case subscription(until: Date)

    var expirationDate: Date? {
        if case let .subscription(until) = self { return until }
        return nil
    }

    func isActive(at date: Date) -> Bool { expirationDate.map { $0 > date } ?? true }

    /// 宽限期只接收已验签且处于宽限期的续订状态。
    static func resolve(
        productType: Product.ProductType,
        expirationDate: Date?,
        revocationDate: Date?,
        isUpgraded: Bool,
        gracePeriodExpirationDate: Date?,
        now: Date
    ) -> Self? {
        guard revocationDate == nil, !isUpgraded else { return nil }
        if productType == .nonConsumable { return .lifetime }
        guard productType == .autoRenewable, let expirationDate else { return nil }
        let end = max(expirationDate, gracePeriodExpirationDate ?? expirationDate)
        return end > now ? .subscription(until: end) : nil
    }
}
