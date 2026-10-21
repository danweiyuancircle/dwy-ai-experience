import XCTest
@testable import PurchaseCore

final class PurchaseCoreTests: XCTestCase {
    func testDebugUnlockKey() {
        XCTAssertEqual(PurchaseAccess.debugUnlockKey, "debug.unlockAll")
    }

    func testPurchasedWhenStoreKitSaysSo() {
        XCTAssertTrue(PurchaseAccess.isPurchased(storeKit: true, debugUnlock: false))
        XCTAssertFalse(PurchaseAccess.isPurchased(storeKit: false, debugUnlock: false))
    }

    func testDebugUnlockCountsAsPurchasedInDebug() {
        #if DEBUG
        XCTAssertTrue(PurchaseAccess.isPurchased(storeKit: false, debugUnlock: true))
        XCTAssertTrue(PurchaseAccess.isPurchased(storeKit: true, debugUnlock: true))
        #else
        XCTAssertFalse(PurchaseAccess.isPurchased(storeKit: false, debugUnlock: true))
        #endif
    }

    func testEntitlementRequiresMatchingProductAndNoRevocation() {
        XCTAssertTrue(PurchaseAccess.matchesEntitlement(
            productID: "com.dwy.app.lifetime",
            transactionProductID: "com.dwy.app.lifetime",
            revocationDate: nil
        ))
        XCTAssertFalse(PurchaseAccess.matchesEntitlement(
            productID: "com.dwy.app.lifetime",
            transactionProductID: "com.dwy.other.lifetime",
            revocationDate: nil
        ))
        XCTAssertFalse(PurchaseAccess.matchesEntitlement(
            productID: "com.dwy.app.lifetime",
            transactionProductID: "com.dwy.app.lifetime",
            revocationDate: Date()
        ))
    }

    func testStoreErrorCasesExist() {
        XCTAssertNotNil(StoreError.productUnavailable.errorDescription)
        XCTAssertNotNil(StoreError.unverified.errorDescription)
        XCTAssertNotNil(StoreError.pending.errorDescription)
    }

    @MainActor
    func testDebugUnlockPersistsAndReportsPurchased() {
        let suite = "PurchaseCoreTests.\(UUID().uuidString)"
        let defaults = UserDefaults(suiteName: suite)!
        defaults.removePersistentDomain(forName: suite)

        let store = LifetimeStore(productID: "com.example.app.lifetime", defaults: defaults)
        XCTAssertFalse(store.isPurchased)
        XCTAssertFalse(store.canPurchase)

        #if DEBUG
        var callbackValue: Bool?
        let storeWithCallback = LifetimeStore(
            productID: "com.example.app.lifetime",
            defaults: defaults
        ) { unlocked in
            callbackValue = unlocked
        }
        storeWithCallback.debugUnlockAll = true
        XCTAssertTrue(storeWithCallback.isPurchased)
        XCTAssertTrue(defaults.bool(forKey: PurchaseAccess.debugUnlockKey))
        XCTAssertEqual(callbackValue, true)
        XCTAssertFalse(storeWithCallback.canPurchase)
        #endif
    }
}
