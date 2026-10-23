import Foundation

enum AuthStrings {
    static func text(_ key: String, locale: Locale) -> String {
        let language = locale.language.languageCode?.identifier == "zh" ? "zh-Hans" : "en"
        // SwiftPM 会把资源目录规范化为小写；使用 Bundle 实际支持的标识，兼容 Xcode 与原生构建。
        let localization = Bundle.preferredLocalizations(from: Bundle.module.localizations, forPreferences: [language]).first
        let path = localization.flatMap { Bundle.module.path(forResource: $0, ofType: "lproj") }
        let bundle = path.flatMap(Bundle.init(path:)) ?? .module
        return bundle.localizedString(forKey: key, value: nil, table: nil)
    }
}
