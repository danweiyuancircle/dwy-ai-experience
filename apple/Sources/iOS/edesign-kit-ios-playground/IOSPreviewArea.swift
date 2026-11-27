#if os(iOS)
import SwiftUI
import DesignKitIOS

/// 把预览选项只应用到子树；不调用 ThemeManager，不写用户偏好。
/// 系统弹框（alert）由 UIKit 承载，不跟随子树明暗覆盖，需要验证深色弹框时请切换系统外观。
struct IOSPreviewArea<Content: View>: View {
    let options: IOSPreviewOptions
    @ViewBuilder let content: Content
    @Environment(\.displayScale) private var displayScale

    var body: some View {
        let theme = EControlTheme.standard
        content
            .padding(theme.spacing.group)
            .frame(maxWidth: .infinity, alignment: .leading)
            .background(theme.colors.background, in: RoundedRectangle(cornerRadius: theme.radius.card))
            .overlay {
                RoundedRectangle(cornerRadius: theme.radius.card)
                    .strokeBorder(theme.colors.separator, lineWidth: theme.hairline(displayScale: displayScale))
            }
            .eControlTheme(options.alternateBrand ? Self.alternateTheme : .standard)
            .eControlPlacement(options.floatingPlacement ? .floating : .content)
            .dynamicTypeSize(options.largeText ? .accessibility2 : .large)
            .modifier(SchemeOverride(appearance: options.appearance))
    }

    static var alternateTheme: EControlTheme {
        EControlTheme(accent: EAccentColors(
            light: .indigo, onLight: .white, dark: .cyan, onDark: .black,
            highContrastLight: .black, onHighContrastLight: .white,
            highContrastDark: .white, onHighContrastDark: .black
        ))
    }
}

/// system 不覆盖，继承宿主环境。
private struct SchemeOverride: ViewModifier {
    let appearance: IOSPreviewOptions.Appearance

    func body(content: Content) -> some View {
        switch appearance {
        case .system: content
        case .light: content.environment(\.colorScheme, .light)
        case .dark: content.environment(\.colorScheme, .dark)
        }
    }
}

/// 预览设置面板：切换组件时保留，关闭 Playground 后不保存。
struct IOSPreviewControls: View {
    @Binding var options: IOSPreviewOptions
    @Environment(\.locale) private var locale
    @Environment(\.dismiss) private var dismiss
    @Environment(\.colorScheme) private var systemScheme
    @Environment(\.dynamicTypeSize) private var systemTypeSize
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    @Environment(\.accessibilityReduceTransparency) private var reduceTransparency
    @Environment(\.accessibilityVoiceOverEnabled) private var voiceOver
    @Environment(\.colorSchemeContrast) private var contrast

    var body: some View {
        let text = IOSPlaygroundChrome(locale: locale)
        NavigationStack {
            Form {
                Section {
                    Picker(text("Appearance", "外观"), selection: $options.appearance) {
                        ForEach(IOSPreviewOptions.Appearance.allCases) { item in
                            Text(verbatim: item.title.resolve(locale)).tag(item)
                        }
                    }
                    .accessibilityIdentifier("playground.preview.appearance")
                    Toggle(text("Larger preview text", "预览大字号"), isOn: $options.largeText)
                        .accessibilityIdentifier("playground.preview.large-text")
                    Toggle(text("Alternate brand", "备用品牌色"), isOn: $options.alternateBrand)
                        .accessibilityIdentifier("playground.preview.brand")
                    Toggle(text("Floating placement", "浮动材质"), isOn: $options.floatingPlacement)
                        .accessibilityIdentifier("playground.preview.placement")
                } footer: {
                    Text(verbatim: text("These values only affect the preview area and are not saved.",
                                        "这些值只影响预览区域，不会保存。"))
                }
                Section {
                    Button(text("Use host settings", "恢复宿主设置")) { options.reset() }
                        .disabled(options.isDefault)
                        .accessibilityIdentifier("playground.preview.reset")
                }
                Section(text("System and accessibility", "系统与辅助功能")) {
                    status(text("Effective appearance", "实际外观"), systemScheme == .dark ? text("Dark", "深色") : text("Light", "浅色"))
                    status(text("Effective locale", "实际语言"), locale.identifier)
                    status("Dynamic Type", String(describing: systemTypeSize))
                    status("VoiceOver", voiceOver ? text("On", "开") : text("Off", "关"))
                    status(text("Reduce motion", "减弱动态效果"), reduceMotion ? text("On", "开") : text("Off", "关"))
                    status(text("Reduce transparency", "降低透明度"), reduceTransparency ? text("On", "开") : text("Off", "关"))
                    status(text("Increased contrast", "增强对比度"), contrast == .increased ? text("On", "开") : text("Off", "关"))
                }
            }
            .navigationTitle(text("Preview settings", "预览设置"))
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .confirmationAction) {
                    Button(text("Done", "完成")) { dismiss() }
                }
            }
        }
    }

    private func status(_ title: String, _ value: String) -> some View {
        LabeledContent {
            Text(verbatim: value)
        } label: {
            Text(verbatim: title)
        }
    }
}
#endif
