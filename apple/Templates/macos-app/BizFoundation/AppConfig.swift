import Foundation

// MARK: - ③ 产品常量
// 限额 / 试用规则写旁边的纯函数，不要把 StoreKit 拉进这一层。

/// 本 App 的业务无关配置（product id、隐私、评价、反馈邮箱）。
public enum AppConfig: Sendable {
    /// 终身买断。ASC 建同名 NonConsumable；本地 `App/Products.storekit` 已占位。
    public static let unlockProductID = "__BUNDLE_ID__.lifetime"

    /// 隐私政策中文页。生成后改成真实 slug。
    public static let privacyURLZh = URL(string: "https://unitcircle.tech/zh/products/__APP_NAME__/privacy/privacy")

    /// 隐私政策英文页。
    public static let privacyURLEn = URL(string: "https://unitcircle.tech/en/products/__APP_NAME__/privacy/privacy")

    /// App Store Connect 数字 id（不是 bundle id）。上架后填上，设置「给个好评」才能打开写评价页。
    /// 空着时设置按钮只走系统评价框。
    public static let appStoreID = ""

    /// 直开 App Store 写评价。`appStoreID` 为空则 nil。
    public static var writeReviewURL: URL? {
        guard !appStoreID.isEmpty else { return nil }
        return URL(string: "https://apps.apple.com/app/id\(appStoreID)?action=write-review")
    }

    /// 按界面语言挑隐私 URL。
    public static func privacyURL(localeIdentifier: String) -> URL? {
        if localeIdentifier.lowercased().hasPrefix("zh") { return privacyURLZh }
        return privacyURLEn
    }

    /// 意见反馈收件箱。点设置会 `mailto:` 拉起系统邮箱。
    public static let feedbackEmail = "tianxiake1994@gmail.com"

    /// 预填主题和正文的 mailto。用 URLComponents 编码，避免空格 / 中文把链接拆坏。
    public static func feedbackMailtoURL(subject: String, body: String) -> URL? {
        var components = URLComponents()
        components.scheme = "mailto"
        components.path = feedbackEmail
        components.queryItems = [
            URLQueryItem(name: "subject", value: subject),
            URLQueryItem(name: "body", value: body),
        ]
        return components.url
    }
}
