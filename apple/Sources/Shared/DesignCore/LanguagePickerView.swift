import SwiftUI
import L10nKit

/// 设置页语言行：本页 `Picker(.menu)`，不要 `NavigationLink` 再开一页。
/// 切完语言返回时父页往往不重绘；嵌在当前 `List` 里才能当场换文案。
public struct LanguagePickerView: View {
    @State private var localization = LocalizationManager.shared

    public init() {}

    public var body: some View {
        @Bindable var localization = localization
        LabeledContent {
            Picker(loc("settings_language"), selection: $localization.language) {
                ForEach(localization.supportedLanguages) { lang in
                    Text(lang.displayName).tag(lang)
                }
            }
            .labelsHidden()
            .pickerStyle(.menu)
            .accessibilityLabel(loc("settings_language"))
        } label: {
            Label(loc("settings_language"), systemImage: "globe")
        }
    }
}
