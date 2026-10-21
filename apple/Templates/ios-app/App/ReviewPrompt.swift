import StoreKit
import SwiftUI
import BizFoundation

// MARK: - ① 系统评价框
// 第 3 次进入根页弹一次。设置里「给个好评」再弹。系统有年度次数上限，不保证每次都出。

enum ReviewPrompt {
    private static let launchCountKey = "review.launchCount"

    /// 累计启动并在门槛处调用 `requestReview()`。
    @MainActor
    static func recordLaunch(requestReview: RequestReviewAction) {
        let n = UserDefaults.standard.integer(forKey: launchCountKey) + 1
        UserDefaults.standard.set(n, forKey: launchCountKey)
        if ReviewGate.shouldPrompt(launchCount: n) {
            requestReview()
        }
    }
}
