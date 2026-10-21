import Foundation

/// 当前选定语言对应的 .lproj bundle 快照，供 `loc()` 在任意隔离域读取。
/// 仅 `LocalizationManager` 在 init / 语言变更时写入。
nonisolated(unsafe) private var localizationBundle: Bundle = .main

/// 用当前选定语言解析本地化字符串。
/// 显式传 bundle，不依赖系统 locale 自动解析 key。
///
/// 主线程（SwiftUI `body`）会读 `LocalizationManager.language`，让 Observation
/// 把当前视图登记为语言依赖。只改全局 bundle、不碰 Observable 时，切语言页面不会重绘。
public func loc(_ key: String.LocalizationValue) -> String {
    LocalizationManager.trackLanguageAccess()
    return String(localized: key, bundle: localizationBundle)
}

/// 应用内语言切换中枢：持久化选择、刷新 `localizationBundle`、暴露 `locale`。
/// 根视图须 `@State` / `@Environment` 持有本实例，并注入 `.environment(\.locale, localization.locale)`。
/// `loc()` 已在主线程登记 `language`；未升到含此修复的 kit 时，各 View.body 仍须 `let _ = localization.language`。
///
/// 启动早期可调用 `configure(supported:)` 收窄设置页语言列表；默认中英 + 跟随系统。
@MainActor
@Observable
public final class LocalizationManager {
    public static let shared = LocalizationManager()

    /// `loc()` 在 View.body 求值时走这里，把当前观察上下文登记到 `language`。
    /// 后台线程调用 loc（测试 / 导出）跳过，避免跨隔离域读 MainActor 状态。
    nonisolated static func trackLanguageAccess() {
        guard Thread.isMainThread else { return }
        MainActor.assumeIsolated {
            _ = LocalizationManager.shared.language
        }
    }

    /// 持久化键。
    private static let languageKey = "settings.language"

    /// 设置页展示的语言列表（含 `.system`）。默认中英，App 可 configure 覆盖。
    public private(set) var supportedLanguages: [AppLanguage] = [.system, .zhHans, .en]

    /// 用于「跟随系统」解析的资源 code 列表（不含 system）。
    public private(set) var supportedCodes: [String] = ["zh-Hans", "en"]

    /// 当前语言。写入即持久化并刷新 bundle 快照。
    public var language: AppLanguage {
        didSet {
            // 不在 supported 内则回退 system，避免配置收窄后读到旧值卡死。
            if !supportedLanguages.contains(language), language != .system {
                language = .system
                return
            }
            UserDefaults.standard.set(language.rawValue, forKey: Self.languageKey)
            localizationBundle = Self.bundle(for: language, supportedCodes: supportedCodes)
        }
    }

    /// 注入根视图的 locale；日期数字格式与界面语言一致。
    public var locale: Locale {
        if let code = language.code {
            return Locale(identifier: code)
        }
        return Locale(identifier: resolvedSystemCode())
    }

    private init() {
        let saved = UserDefaults.standard.string(forKey: Self.languageKey)
        language = saved.flatMap(AppLanguage.init(rawValue:)) ?? .system
        localizationBundle = Self.bundle(for: language, supportedCodes: supportedCodes)
    }

    /// 配置本 App 支持的语言（设置页列表 + 系统回落匹配）。
    /// - Parameter languages: 须包含至少一种带 code 的语言；可含 `.system`。
    /// - Note: 建议在 `@main` init 最早调用，且只调用一次。
    public func configure(supported languages: [AppLanguage]) {
        var list = languages
        if !list.contains(.system) {
            list.insert(.system, at: 0)
        }
        let codes = list.compactMap(\.code)
        precondition(!codes.isEmpty, "supported languages must include at least one resource language")
        supportedLanguages = list
        supportedCodes = codes
        // 重新解析当前选择 / bundle。
        let current = language
        language = list.contains(current) ? current : .system
        localizationBundle = Self.bundle(for: language, supportedCodes: supportedCodes)
    }

    /// 从系统首选语言列表里挑一个我们支持的 code。
    public func resolvedSystemCode() -> String {
        Self.resolveSystemCode(supportedCodes: supportedCodes)
    }

    /// 取指定语言 .lproj；`.system` 解析为支持的系统首选；缺失回退 `.main`。
    private static func bundle(for language: AppLanguage, supportedCodes: [String]) -> Bundle {
        let code: String?
        switch language {
        case .system:
            code = resolveSystemCode(supportedCodes: supportedCodes)
        default:
            code = language.code
        }
        guard
            let code,
            let path = Bundle.main.path(forResource: code, ofType: "lproj"),
            let bundle = Bundle(path: path)
        else {
            return .main
        }
        return bundle
    }

    /// 系统首选 → 支持的 code。简繁分流；未知回退列表首项或 zh-Hans。
    /// 纯函数，可非隔离调用（单测 / 任意线程）。
    nonisolated static func resolveSystemCode(supportedCodes: [String]) -> String {
        let supported = Set(supportedCodes)
        for preferred in Locale.preferredLanguages {
            let lower = preferred.lowercased()
            if lower.hasPrefix("zh") {
                // 繁体线索：Hant / TW / HK / MO。
                let isHant = lower.contains("hant")
                    || lower.contains("tw")
                    || lower.contains("hk")
                    || lower.contains("mo")
                if isHant, supported.contains("zh-Hant") { return "zh-Hant" }
                if supported.contains("zh-Hans") { return "zh-Hans" }
                if supported.contains("zh-Hant") { return "zh-Hant" }
                continue
            }
            // en-US → en
            let base = String(lower.prefix(while: { $0 != "-" && $0 != "_" }))
            if let match = supportedCodes.first(where: { $0.lowercased() == base || $0.lowercased().hasPrefix(base) }) {
                return match
            }
        }
        return supportedCodes.first ?? "zh-Hans"
    }
}
