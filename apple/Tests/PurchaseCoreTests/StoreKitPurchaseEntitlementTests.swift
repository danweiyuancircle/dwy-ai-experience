#if canImport(StoreKit)
import Foundation
import StoreKit
import XCTest
@testable import PurchaseCore

final class StoreKitPurchaseEntitlementTests: XCTestCase {
    private let now = Date(timeIntervalSince1970: 1_000)

    func testLifetimeOnlyGrantsAccessWhileUnrevoked() {
        XCTAssertEqual(resolve(.nonConsumable), .lifetime)
        XCTAssertNil(resolve(.nonConsumable, revocation: now))
        XCTAssertNil(resolve(.consumable))
    }

    func testSubscriptionEndsAtExpirationOrVerifiedGracePeriod() {
        let expiration = now.addingTimeInterval(60)
        let grace = expiration.addingTimeInterval(120)
        XCTAssertEqual(resolve(.autoRenewable, expiration: expiration), .subscription(until: expiration))
        XCTAssertEqual(resolve(.autoRenewable, expiration: now, grace: grace), .subscription(until: grace))
        XCTAssertNil(resolve(.autoRenewable, expiration: now))
        XCTAssertNil(resolve(.autoRenewable, expiration: now.addingTimeInterval(-60), grace: now))
        XCTAssertNil(resolve(.autoRenewable, grace: grace))
    }

    func testRevocationOrUpgradeOverridesAnActiveSubscription() {
        let expiration = now.addingTimeInterval(60)
        XCTAssertNil(resolve(.autoRenewable, expiration: expiration, revocation: now))
        XCTAssertNil(resolve(.autoRenewable, expiration: expiration, upgraded: true))
    }

    func testStoreErrorDisplaysMessageWhenHostTranslationIsMissing() {
        XCTAssertEqual(StoreError.productUnavailable.errorDescription, "This product is unavailable.")
    }

    @MainActor
    func testPurchaseRejectsAnUnconfiguredIDBeforeCallingStoreKit() async {
        let store = StoreKitPurchaseStore(productTypes: ["demo.lifetime": .nonConsumable])
        do {
            _ = try await store.purchase("another-product")
            XCTFail("The store accepted a product outside the configured catalog")
        } catch StoreError.productUnavailable {
            XCTAssertFalse(store.hasLoadedEntitlements)
            XCTAssertFalse(store.isPurchasing)
        } catch {
            XCTFail("Unexpected error: \(error)")
        }
    }

    private func resolve(
        _ type: Product.ProductType,
        expiration: Date? = nil,
        revocation: Date? = nil,
        upgraded: Bool = false,
        grace: Date? = nil
    ) -> StoreKitPurchaseEntitlement? {
        StoreKitPurchaseEntitlement.resolve(
            productType: type,
            expirationDate: expiration,
            revocationDate: revocation,
            isUpgraded: upgraded,
            gracePeriodExpirationDate: grace,
            now: now
        )
    }
}
#endif
