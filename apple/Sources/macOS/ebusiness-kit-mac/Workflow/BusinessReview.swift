#if os(macOS)
import DesignKitMac
import Foundation
import StoreKit
import SwiftUI

/// 按业务成功事件累计评分机会。宿主只在用户实际完成一项操作后调用。
@MainActor
public final class BusinessReviewPrompter {
    private let defaults: UserDefaults
    private let storageKey: String
    private let threshold: Int
    private let cooldown: TimeInterval

    /// 计数和上一次请求的时间一起保存。storageKey 在应用内应唯一。
    public init(
        storageKey: String,
        defaults: UserDefaults = .standard,
        minimumSuccessfulEvents: Int = 3,
        cooldown: TimeInterval = 90 * 24 * 60 * 60
    ) {
        precondition(!storageKey.isEmpty && minimumSuccessfulEvents > 0 && cooldown.isFinite && cooldown >= 0)
        self.defaults = defaults
        self.storageKey = storageKey
        self.threshold = minimumSuccessfulEvents
        self.cooldown = cooldown
    }

    /// 记录事件并消费本次评分机会。返回 true 表示可以请求，系统仍决定是否展示。
    @discardableResult
    public func recordSuccessfulEvent(now: Date = .now) -> Bool {
        var stored = defaults.dictionary(forKey: storageKey) ?? [:]
        let count = min(max(stored["count"] as? Int ?? 0, 0), threshold - 1) + 1
        let cooledDown = (stored["requestedAt"] as? Date).map { now.timeIntervalSince($0) >= cooldown } ?? true
        let shouldRequest = count == threshold && cooledDown
        stored["count"] = shouldRequest ? 0 : count
        if shouldRequest { stored["requestedAt"] = now }
        defaults.set(stored, forKey: storageKey)
        return shouldRequest
    }

    /// 在当前 SwiftUI 窗口的业务成功回调中传入环境的 requestReview。
    public func recordSuccessfulEvent(requestReview: RequestReviewAction, now: Date = .now) {
        if recordSuccessfulEvent(now: now) { requestReview() }
    }
}

/// 手动打开宿主提供的商店评价链接，与自动提示的计数和冷却独立。
public struct BusinessReviewRow: View {
    private let url: URL

    public init(url: URL) { self.url = url }

    public var body: some View {
        ESettingsRow(workflowText("review.title")) {
            Link(destination: url) { workflowText("review.open") }
        }
    }
}
#endif
