#if os(macOS)
import DesignCore
import DesignKitMac
import L10nKit
import SwiftUI

/// 通用设置页内容。默认本机保存，也可绑定应用的云端设置入口。
public struct BusinessGeneralSettings<Language: Hashable & Identifiable>: View {
    @Binding private var language: Language
    @Binding private var appearance: ThemeMode
    @Binding private var textSize: BusinessTextSize
    @Environment(\.eControlTheme) private var theme
    private let languages: [Language]
    private let languageTitle: Text
    private let appearanceTitle: Text
    private let languageName: (Language) -> Text
    private let appearanceName: (ThemeMode) -> Text

    /// 使用默认语言、外观及字号能力，设置改动立即通知应用。
    public init(preferences: BusinessPreferences) where Language == AppLanguage {
        @Bindable var localization = preferences.localization
        @Bindable var theme = preferences.appearance
        @Bindable var preferences = preferences
        self.init(languages: localization.supportedLanguages, language: $localization.language,
                  appearance: $theme.mode, textSize: $preferences.textSize)
    }

    /// 自有存储使用绑定提供当前已生效值，并在写入时调用既有保存流程。
    public init(
        languages: [AppLanguage],
        language: Binding<AppLanguage>,
        appearance: Binding<ThemeMode>,
        textSize: Binding<BusinessTextSize>
    ) where Language == AppLanguage {
        self.init(
            languages: languages,
            language: language,
            appearance: appearance,
            textSize: textSize,
            languageTitle: Text("Language", tableName: "Settings", bundle: .module),
            appearanceTitle: Text("Appearance", tableName: "Settings", bundle: .module),
            languageName: Self.standardLanguageName,
            appearanceName: Self.standardAppearanceName
        )
    }

    /// 已有语言模型与译文的应用可保留原来的区域代码、资源标签及保存行为。
    public init(
        languages: [Language],
        language: Binding<Language>,
        appearance: Binding<ThemeMode>,
        textSize: Binding<BusinessTextSize>,
        languageTitle: Text,
        appearanceTitle: Text,
        languageName: @escaping (Language) -> Text,
        appearanceName: @escaping (ThemeMode) -> Text
    ) {
        self.languages = languages
        _language = language
        _appearance = appearance
        _textSize = textSize
        self.languageTitle = languageTitle
        self.appearanceTitle = appearanceTitle
        self.languageName = languageName
        self.appearanceName = appearanceName
    }

    public var body: some View {
        let textSizeTitle = Text("Text Size", tableName: "Settings", bundle: .module)
        ECard {
            VStack(spacing: theme.spacing.formRow) {
                ESettingsRow(languageTitle) {
                    EPicker(languageTitle, selection: $language, selectedLabel: languageName, maxLabelWidth: 100) {
                        ForEach(languages) { candidate in
                            languageName(candidate).tag(candidate)
                        }
                    }
                }
                Divider()
                ESettingsRow(appearanceTitle) {
                    EPicker(appearanceTitle, selection: $appearance, selectedLabel: appearanceName) {
                        ForEach(ThemeMode.allCases) { mode in
                            appearanceName(mode).tag(mode)
                        }
                    }
                }
                Divider()
                ESettingsRow(textSizeTitle) {
                    EPicker(textSizeTitle, selection: $textSize, selectedLabel: { $0.title }) {
                        ForEach(BusinessTextSize.allCases) { size in
                            size.title.tag(size)
                        }
                    }
                }
            }
        }
    }

    private static func standardLanguageName(_ candidate: AppLanguage) -> Text {
        candidate == .system ? Text("Use System Setting", tableName: "Settings", bundle: .module)
            : Text(verbatim: candidate.displayName)
    }

    private static func standardAppearanceName(_ mode: ThemeMode) -> Text {
        switch mode {
        case .system: Text("Use System Setting", tableName: "Settings", bundle: .module)
        case .light: Text("Light", tableName: "Settings", bundle: .module)
        case .dark: Text("Dark", tableName: "Settings", bundle: .module)
        }
    }
}

/// 关于页面组合。版本信息来自宿主，产品链接由应用配置。
public struct BusinessAboutSettings: View {
    private let bundle: Bundle
    private let privacyURL: URL?
    private let supportURL: URL?

    /// 隐私和支持链接按宿主实际配置显示。
    public init(bundle: Bundle = .main, privacyURL: URL? = nil, supportURL: URL? = nil) {
        self.bundle = bundle
        self.privacyURL = privacyURL
        self.supportURL = supportURL
    }

    public var body: some View {
        ECard {
            ELabelValue(
                Text("Version", tableName: "Settings", bundle: .module),
                value: Text(verbatim: version)
            )
            if let privacyURL {
                Divider()
                Link(destination: privacyURL) {
                    Text("Privacy Policy", tableName: "Settings", bundle: .module)
                }
            }
            if let supportURL {
                Divider()
                Link(destination: supportURL) {
                    Text("Support", tableName: "Settings", bundle: .module)
                }
            }
        }
    }

    private var version: String {
        let short = bundle.object(forInfoDictionaryKey: "CFBundleShortVersionString") as? String
        let build = bundle.object(forInfoDictionaryKey: "CFBundleVersion") as? String
        if let short, let build, short != build { return "\(short) (\(build))" }
        return short ?? build ?? "—"
    }
}
#endif
