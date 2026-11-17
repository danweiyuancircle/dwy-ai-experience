import Foundation

/// 终身买断的纯判断。StoreKit 交易解析和 DEBUG 开关都走这里，方便单测。
public enum PurchaseAccess: Sendable {
    /// DEBUG 解锁的 UserDefaults 键。各 App 必须用这一把，禁止另起名字。
    public static let debugUnlockKey = "debug.unlockAll"

    /// UI / 门控看到的「是否已购」。
    /// Release 忽略 `debugUnlock`，避免商店包被开关放行。
    public static func isPurchased(storeKit: Bool, debugUnlock: Bool) -> Bool {
        _ = debugUnlock
        #if DEBUG
        if debugUnlock { return true }
        #endif
        return storeKit
    }

    /// 当前权益是否覆盖该终身商品：productID 一致且未被撤销。
    public static func matchesEntitlement(
        productID: String,
        transactionProductID: String,
        revocationDate: Date?
    ) -> Bool {
        transactionProductID == productID && revocationDate == nil
    }
}
