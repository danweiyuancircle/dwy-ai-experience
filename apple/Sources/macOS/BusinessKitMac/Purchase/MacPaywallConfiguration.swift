#if os(macOS)
import Foundation
import PurchaseCore

/// 弹框的商品展示文案。ID 必须对应真实商品，价格由购买服务提供。
public struct MacPaywallPlan: Identifiable {
    public let id: String
    public let title: String
    public let detail: String?
    public let isRecommended: Bool
    public let purchaseTitle: String?
    public let priceSuffix: String?

    /// priceSuffix 可附加在 StoreKit 本地化价格后，说明计费周期和续订条款。
    public init(
        id: String,
        title: String,
        detail: String? = nil,
        isRecommended: Bool = false,
        purchaseTitle: String? = nil,
        priceSuffix: String? = nil
    ) {
        self.id = id
        self.title = title
        self.detail = detail
        self.isRecommended = isRecommended
        self.purchaseTitle = purchaseTitle
        self.priceSuffix = priceSuffix
    }
}

/// 一条权益对比。缺省列表示该档未提供此权益。
public struct MacPaywallFeature {
    public let title: String
    public let free: String?
    public let paid: String?

    public init(title: String, free: String? = nil, paid: String? = nil) {
        self.title = title
        self.free = free
        self.paid = paid
    }
}

/// 每个弹框独立的展示配置。调用方传入当前语言的文本和协议链接。
public struct MacPaywallConfiguration {
    public let title: String
    public let subtitle: String?
    public let plans: [MacPaywallPlan]
    public let features: [MacPaywallFeature]
    public let termsURL: URL?
    public let privacyURL: URL?
    public let restoreProductIDs: Set<String>

    public init(
        title: String,
        subtitle: String? = nil,
        plans: [MacPaywallPlan],
        features: [MacPaywallFeature] = [],
        termsURL: URL? = nil,
        privacyURL: URL? = nil,
        restoreProductIDs: Set<String>? = nil
    ) {
        self.title = title
        self.subtitle = subtitle
        var seen = Set<String>()
        self.plans = plans.filter { !$0.id.isEmpty && seen.insert($0.id).inserted }
        self.features = features
        self.termsURL = termsURL
        self.privacyURL = privacyURL
        // 宿主可隐藏已持有的订阅方案，但恢复时仍检查这些商品。
        self.restoreProductIDs = restoreProductIDs ?? Set(self.plans.map(\.id))
    }
}

/// 支付服务此刻的真实价格和有效权益。价格为空的商品不会触发购买。
public struct MacPaywallSnapshot {
    public let prices: [String: String]
    public let purchasedProductIDs: Set<String>
    public let loadError: String?

    public init(prices: [String: String], purchasedProductIDs: Set<String> = [], loadError: String? = nil) {
        self.prices = prices.filter { !$0.value.isEmpty }
        self.purchasedProductIDs = purchasedProductIDs
        self.loadError = loadError
    }
}

/// 主线程支付接点。自有服务应在购买或恢复返回前更新可观察快照。
@MainActor
public struct MacPaywallStore {
    let snapshot: @MainActor () -> MacPaywallSnapshot
    let load: @MainActor () async throws -> Void
    let purchase: @MainActor (String) async throws -> StoreKitPurchaseOutcome
    let restore: @MainActor () async throws -> Void

    /// 保留应用现有支付服务。购后只依据 snapshot 的有效权益关闭弹框。
    public init(
        snapshot: @escaping @MainActor () -> MacPaywallSnapshot,
        load: @escaping @MainActor () async throws -> Void,
        purchase: @escaping @MainActor (String) async throws -> StoreKitPurchaseOutcome,
        restore: @escaping @MainActor () async throws -> Void
    ) {
        self.snapshot = snapshot
        self.load = load
        self.purchase = purchase
        self.restore = restore
    }

    /// 接入现有的单商品买断服务，可继续使用应用持有的实例。
    public init(lifetimeStore store: LifetimeStore) {
        self.init(
            snapshot: {
                MacPaywallSnapshot(
                    prices: store.priceText.map { [store.productID: $0] } ?? [:],
                    purchasedProductIDs: store.isPurchased ? [store.productID] : [],
                    loadError: store.productLoadError
                )
            },
            load: { await store.reloadProduct() },
            purchase: { id in
                guard id == store.productID else { throw StoreError.productUnavailable }
                do { return try await store.purchase() ? .purchased : .cancelled }
                catch StoreError.pending { return .pending }
            },
            restore: { try await store.restore() }
        )
    }

    /// 直接对接支持买断与订阅的 StoreKit 服务。
    public init(storeKitStore store: StoreKitPurchaseStore) {
        self.init(
            snapshot: {
                MacPaywallSnapshot(
                    prices: Dictionary(uniqueKeysWithValues: store.products.map { ($0.id, $0.displayPrice) }),
                    purchasedProductIDs: store.purchasedProductIDs,
                    loadError: store.productLoadError ?? store.entitlementError
                )
            },
            load: { await store.reloadProducts() },
            purchase: { id in try await store.purchase(id) },
            restore: { try await store.restore() }
        )
    }
}
#endif
