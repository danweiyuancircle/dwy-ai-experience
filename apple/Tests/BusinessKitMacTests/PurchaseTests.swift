#if os(macOS)
import StoreKit
import XCTest
@testable import BusinessKitMac

@MainActor
final class PurchaseTests: XCTestCase {
    private let productID = "demo.annual"

    func testPurchaseOnlyReturnsVerifiedAccessOnceAfterDismissal() async throws {
        let flow = MacPaywallFlow()
        let id = productID
        var owned = Set<String>()
        let store = MacPaywallStore(
            snapshot: { .init(prices: [id: "$19.99"], purchasedProductIDs: owned) },
            load: {},
            purchase: { productID in
                owned.insert(productID)
                return .purchased
            },
            restore: {}
        )
        flow.begin()
        let shouldClose = await flow.buy(id, store: store)
        XCTAssertTrue(shouldClose)
        XCTAssertEqual(flow.dismissed(), [id])
        XCTAssertTrue(flow.dismissed().isEmpty)
    }

    func testPendingWaitsForTheSelectedEntitlementAndCancellationKeepsTheSheet() async {
        let flow = MacPaywallFlow()
        let id = productID
        let pending = MacPaywallStore(
            snapshot: { .init(prices: [id: "$19.99"]) },
            load: {}, purchase: { _ in .pending }, restore: {}
        )
        flow.begin()
        let closedForPending = await flow.buy(id, store: pending)
        XCTAssertFalse(closedForPending)
        XCTAssertFalse(flow.confirmPending(["demo.monthly"]))
        XCTAssertTrue(flow.confirmPending([id]))
        XCTAssertEqual(flow.dismissed(), [id])

        let cancelled = MacPaywallStore(
            snapshot: { .init(prices: [id: "$19.99"]) },
            load: {}, purchase: { _ in .cancelled }, restore: {}
        )
        flow.begin()
        let closedForCancellation = await flow.buy(id, store: cancelled)
        XCTAssertFalse(closedForCancellation)
        XCTAssertTrue(flow.dismissed().isEmpty)
    }

    func testRestoreOnlyReturnsConfiguredProducts() async {
        let flow = MacPaywallFlow()
        let id = productID
        var owned = Set<String>()
        let store = MacPaywallStore(
            snapshot: { .init(prices: [:], purchasedProductIDs: owned) },
            load: {}, purchase: { _ in .cancelled },
            restore: { owned = [id, "different.product"] }
        )
        flow.begin()
        let shouldClose = await flow.restore(configured: [id], store: store)
        XCTAssertTrue(shouldClose)
        XCTAssertEqual(flow.dismissed(), [id])
    }

    func testRestoreCancellationDoesNotReportExistingAccess() async {
        let flow = MacPaywallFlow()
        let id = productID
        let store = MacPaywallStore(
            snapshot: { .init(prices: [:], purchasedProductIDs: [id]) },
            load: {}, purchase: { _ in .cancelled },
            restore: { throw StoreKitError.userCancelled }
        )
        flow.begin()
        let shouldClose = await flow.restore(configured: [id], store: store)
        XCTAssertFalse(shouldClose)
        XCTAssertNil(flow.notice)
        XCTAssertTrue(flow.dismissed().isEmpty)
    }

    func testReportsWithoutEffectiveAccessDoNotCloseTheSheet() async {
        let flow = MacPaywallFlow()
        let id = productID
        let store = MacPaywallStore(
            snapshot: { .init(prices: [id: "$19.99"], purchasedProductIDs: ["different.product"]) },
            load: {}, purchase: { _ in .purchased }, restore: {}
        )
        flow.begin()
        let purchased = await flow.buy(id, store: store)
        let restored = await flow.restore(configured: [id], store: store)
        XCTAssertFalse(purchased)
        XCTAssertFalse(restored)
        XCTAssertTrue(flow.dismissed().isEmpty)
    }

    func testLatePurchaseResultCannotCloseTheNextSheet() async {
        let flow = MacPaywallFlow()
        let id = productID
        var owned = Set<String>()
        let store = MacPaywallStore(
            snapshot: { .init(prices: [id: "$19.99"], purchasedProductIDs: owned) },
            load: {},
            purchase: { _ in
                _ = flow.dismissed()
                flow.begin()
                owned.insert(id)
                return .purchased
            },
            restore: {}
        )
        flow.begin()
        let shouldClose = await flow.buy(id, store: store)
        XCTAssertFalse(shouldClose)
        XCTAssertEqual(owned, [id])
        XCTAssertTrue(flow.dismissed().isEmpty)
    }

    func testLateRestoreAndPriorDisappearanceCannotAffectTheNextSheet() async {
        let flow = MacPaywallFlow()
        let id = productID
        let original = flow.begin()
        var current: Int?
        let store = MacPaywallStore(
            snapshot: { .init(prices: [:], purchasedProductIDs: [id]) },
            load: {}, purchase: { _ in .cancelled },
            restore: {
                _ = flow.dismissed()
                current = flow.begin()
                flow.deactivate(original)
            }
        )
        let shouldClose = await flow.restore(configured: [id], store: store)
        XCTAssertFalse(shouldClose)
        XCTAssertFalse(flow.isCurrent(original))
        XCTAssertTrue(flow.isCurrent(current))
        XCTAssertTrue(flow.dismissed().isEmpty)
    }
}
#endif
