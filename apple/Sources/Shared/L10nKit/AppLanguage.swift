import Foundation

/// 应用内可选语言。`.system` 跟随系统，其余强制指定，免重启切换。
///
/// 枚举覆盖常见目标市场；App 可用 `LocalizationManager.configure(supported:)` 收窄设置页列表，
/// 与 `CFBundleLocalizations` / xcstrings 对齐即可。
public enum AppLanguage: String, CaseIterable, Identifiable, Sendable {
    case system
    case zhHans
    case zhHant
    case en
    case ja
    case ko
    case de
    case fr
    case es

    public var id: String { rawValue }

    /// 对应 .lproj / Locale code；`.system` 为 nil（不强制资源）。
    public var code: String? {
        switch self {
        case .system: nil
        case .zhHans: "zh-Hans"
        case .zhHant: "zh-Hant"
        case .en: "en"
        case .ja: "ja"
        case .ko: "ko"
        case .de: "de"
        case .fr: "fr"
        case .es: "es"
        }
    }

    /// 选择列表展示名。语言项用母语名（endonym）；仅「跟随系统」走 loc。
    public var displayName: String {
        switch self {
        case .system: loc("language_system")
        case .zhHans: "简体中文"
        case .zhHant: "繁體中文"
        case .en: "English"
        case .ja: "日本語"
        case .ko: "한국어"
        case .de: "Deutsch"
        case .fr: "Français"
        case .es: "Español"
        }
    }

    /// 除 `.system` 外、带资源 code 的语言。
    public static var resourceLanguages: [AppLanguage] {
        allCases.filter { $0.code != nil }
    }
}
