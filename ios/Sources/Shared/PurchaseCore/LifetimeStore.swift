import Foundation
import StoreKit
import Observation

/// StoreKit 2 终身买断（NonConsumable）+ DEBUG 解锁。
///
/// 试用天数、免费次数、App Group 写入都不是本类型的职责。
/// 需要同步扩展 / License 时传入 `onEntitlementChange`。
///
/// 不在 `init` 打 StoreKit；`startIfNeeded()` 懒加载。
@Observable
@MainActor
public final class LifetimeStore {
    /// ASC / `.storekit` 里的终身商品 ID。
    public let productID: String

    /// StoreKit 真实买断。不含 DEBUG 开关。
    public private(set) var storeKitPurchased = false
    /// 当前可购商品；nil 表示还没拉到。
    public private(set) var product: Product?
    public private(set) var isLoadingProduct = false
    public private(set) var isPurchasing = false
    public private(set) var productLoadError: String?

    #if DEBUG
    /// 仅 Debug：视为已购，方便截图 / 验门控。Release 无此字段。
    public var debugUnlockAll: Bool {
        didSet {
            defaults.set(debugUnlockAll, forKey: PurchaseAccess.debugUnlockKey)
            onEntitlementChange?(isPurchased)
        }
    }
    #endif

    private var didStart = false
    private let defaults: UserDefaults
    private let onEntitlementChange: (@MainActor (Bool) -> Void)?

    /// UI 唯一入口：DEBUG 时 OR 调试开关。
    public var isPurchased: Bool {
        #if DEBUG
        PurchaseAccess.isPurchased(storeKit: storeKitPurchased, debugUnlock: debugUnlockAll)
        #else
        PurchaseAccess.isPurchased(storeKit: storeKitPurchased, debugUnlock: false)
        #endif
    }

    /// 未购、有商品、未在购买中才可点买。
    public var canPurchase: Bool {
        !isPurchased && product != nil && !isPurchasing
    }

    /// 系统本地化价格；没拉到就是 nil，禁止假价占位。
    public var priceText: String? {
        let raw = product?.displayPrice
        if let raw, raw.isEmpty { return nil }
        return raw
    }

    public init(
        productID: String,
        defaults: UserDefaults = .standard,
        onEntitlementChange: (@MainActor (Bool) -> Void)? = nil
    ) {
        self.productID = productID
        self.defaults = defaults
        self.onEntitlementChange = onEntitlementChange
        #if DEBUG
        self.debugUnlockAll = defaults.bool(forKey: PurchaseAccess.debugUnlockKey)
        #endif
    }

    /// 幂等：拉商品、扫权益、听后续交易。
    public func startIfNeeded() {
        guard !didStart else { return }
        didStart = true
        Task(priority: .utility) { [weak self] in
            await self?.start()
        }
    }

    /// 发起买断。用户取消返回 false 不抛；失败抛 `StoreError`。
    @discardableResult
    public func purchase() async throws -> Bool {
        startIfNeeded()
        if product == nil { await loadProduct() }
        guard let product else { throw StoreError.productUnavailable }
        isPurchasing = true
        defer { isPurchasing = false }
        let result = try await product.purchase()
        switch result {
        case let .success(.verified(transaction)):
            await transaction.finish()
            storeKitPurchased = true
            onEntitlementChange?(isPurchased)
            return true
        case .success(.unverified):
            throw StoreError.unverified
        case .userCancelled:
            return false
        case .pending:
            throw StoreError.pending
        @unknown default:
            return false
        }
    }

    /// 恢复购买：同步 App Store 后重扫权益。
    public func restore() async throws {
        startIfNeeded()
        try await AppStore.sync()
        await updateEntitlements()
    }

    /// 付费墙「重试」：再拉一次商品。
    public func reloadProduct() async {
        startIfNeeded()
        await loadProduct()
    }

    private func start() async {
        await loadProduct()
        await updateEntitlements()
        for await update in Transaction.updates {
            if case let .verified(transaction) = update {
                await transaction.finish()
                await updateEntitlements()
            }
        }
    }

    private func loadProduct() async {
        isLoadingProduct = true
        defer { isLoadingProduct = false }
        do {
            let products = try await Product.products(for: [productID])
            product = products.first { !$0.displayPrice.isEmpty } ?? products.first
            productLoadError = product == nil ? StoreError.productUnavailable.localizedDescription : nil
        } catch {
            product = nil
            productLoadError = error.localizedDescription
        }
    }

    private func updateEntitlements() async {
        var owned = false
        for await result in Transaction.currentEntitlements {
            if case let .verified(transaction) = result,
               PurchaseAccess.matchesEntitlement(
                productID: productID,
                transactionProductID: transaction.productID,
                revocationDate: transaction.revocationDate
               )
            {
                owned = true
            }
        }
        storeKitPurchased = owned
        onEntitlementChange?(isPurchased)
    }
}
