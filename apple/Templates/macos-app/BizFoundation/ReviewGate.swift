import Foundation

// MARK: - ③ 系统评价框门槛
// 不碰 StoreKit。第几次启动再请评，避免首启打扰。

/// 使用中弹出系统评价框的纯门槛。UI 层 `requestReview()` 才真正弹。
public enum ReviewGate: Sendable {
    /// 第几次冷启动请评。只命中这一次，不是每次 3 的倍数。
    public static let promptAtLaunchCount = 3

    /// 当前累计启动次数是否该弹系统评价框。
    public static func shouldPrompt(launchCount: Int) -> Bool {
        launchCount == promptAtLaunchCount
    }
}
