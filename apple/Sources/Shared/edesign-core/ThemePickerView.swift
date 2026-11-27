import SwiftUI
import L10nKit

/// 设置页外观行：本页 `Picker(.menu)`，不要 `NavigationLink` 再开一页。
/// 根视图配合：`.preferredColorScheme(theme.preferredColorScheme)` + 平台 `ThemeManager`。
///
/// ```swift
/// @Bindable var theme = ThemeManager.shared
/// ThemePickerView(mode: $theme.mode)
/// ```
public struct ThemePickerView: View {
    @Binding private var mode: ThemeMode

    public init(mode: Binding<ThemeMode>) {
        _mode = mode
    }

    public var body: some View {
        LabeledContent {
            Picker(loc("settings_theme"), selection: $mode) {
                ForEach(ThemeMode.allCases) { item in
                    Text(item.displayName).tag(item)
                }
            }
            .labelsHidden()
            .pickerStyle(.menu)
            .accessibilityLabel(loc("settings_theme"))
        } label: {
            Label(loc("settings_theme"), systemImage: "circle.lefthalf.filled")
        }
    }
}
