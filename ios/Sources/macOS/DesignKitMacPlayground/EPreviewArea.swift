#if os(macOS)
import SwiftUI
import AppKit
import DesignKitMac

/// 仅局部预览值；不写入 ThemeManager、LocalizationManager 或 UserDefaults。
struct EPreviewOptions: Equatable {
    var appearance = 0
    var language = 0
    var largeText = false
    var placement = 0

    var scheme: ColorScheme? { appearance == 0 ? nil : appearance == 1 ? .light : .dark }
    var locale: Locale? { language == 0 ? nil : Locale(identifier: language == 1 ? "en" : "zh-Hans") }
    var controlPlacement: EControlPlacement? {
        switch placement {
        case 1: .content
        case 2: .toolbar
        case 3: .floating
        default: nil
        }
    }
}

struct EPreviewControls: View {
    @Binding var options: EPreviewOptions
    @State private var showSystemInformation = false
    @Environment(\.accessibilityVoiceOverEnabled) private var voiceOver
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    @Environment(\.accessibilityReduceTransparency) private var reduceTransparency
    @Environment(\.colorSchemeContrast) private var contrast
    @Environment(\.colorScheme) private var inheritedScheme
    @Environment(\.locale) private var inheritedLocale

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Preview settings", bundle: .module).font(.headline)
            EPicker(resource("Appearance"), selection: $options.appearance) {
                Text("Inherit", bundle: .module).tag(0)
                Text("Light", bundle: .module).tag(1)
                Text("Dark", bundle: .module).tag(2)
            }.accessibilityIdentifier("playground.preview.appearance")
            EPicker(resource("Language"), selection: $options.language) {
                Text("Inherit", bundle: .module).tag(0)
                Text("English", bundle: .module).tag(1)
                Text("简体中文", bundle: .module).tag(2)
            }.accessibilityIdentifier("playground.preview.locale")
            ESwitch(resource("Larger preview text"), isOn: $options.largeText)
                .accessibilityIdentifier("playground.preview.large-text")
            EPicker(resource("Material placement"), selection: $options.placement) {
                Text("Inherit", bundle: .module).tag(0)
                Text("Content", bundle: .module).tag(1)
                Text("Toolbar", bundle: .module).tag(2)
                Text("Floating", bundle: .module).tag(3)
            }.accessibilityIdentifier("playground.preview.placement")
            EButton(resource("Use host settings")) { options = EPreviewOptions() }
                .accessibilityIdentifier("playground.preview.reset")
            DisclosureGroup(isExpanded: $showSystemInformation) {
                VStack(alignment: .leading, spacing: 8) {
                    Text(verbatim: ProcessInfo.processInfo.operatingSystemVersionString)
                    LabeledContent {
                        Text((options.scheme ?? inheritedScheme) == .dark ? LocalizedStringKey("Dark") : LocalizedStringKey("Light"), bundle: .module)
                    } label: { Text("Effective appearance", bundle: .module) }
                    LabeledContent {
                        Text(verbatim: (options.locale ?? inheritedLocale).identifier)
                    } label: { Text("Effective locale", bundle: .module) }
                    status("VoiceOver", enabled: voiceOver)
                    status("Reduce motion", enabled: reduceMotion)
                    status("Reduce transparency", enabled: reduceTransparency)
                    status("Increased contrast", enabled: contrast == .increased)
                    Text("Accessibility values are the actual system settings; change them in System Settings to verify behavior", bundle: .module)
                }
                .font(.caption).foregroundStyle(.secondary).padding(.top, 8)
            } label: { Text("System and accessibility", bundle: .module) }
        }
    }

    private func status(_ title: LocalizedStringKey, enabled: Bool) -> some View {
        LabeledContent {
            Text(enabled ? LocalizedStringKey("On") : LocalizedStringKey("Off"), bundle: .module)
        } label: { Text(title, bundle: .module) }
    }

    private func resource(_ key: String.LocalizationValue) -> LocalizedStringResource {
        LocalizedStringResource(key, bundle: .atURL(Bundle.module.bundleURL))
    }
}

struct EPreviewArea<Content: View>: View {
    @Environment(\.eControlTheme) private var inheritedTheme
    @Environment(\.locale) private var inheritedLocale
    @Environment(\.colorScheme) private var inheritedScheme
    @Environment(\.eControlPlacement) private var inheritedPlacement
    @Environment(\.colorSchemeContrast) private var contrast
    let options: EPreviewOptions
    private let content: Content

    init(options: EPreviewOptions, @ViewBuilder content: () -> Content) {
        self.options = options
        self.content = content()
    }

    var body: some View {
        ELocalPreviewHost(scheme: options.scheme ?? inheritedScheme, increasedContrast: contrast == .increased) {
            content
                .font(theme.typography.body)
                .eControlTheme(theme)
                .eControlPlacement(placement)
                .padding(16)
                .background(theme.colors.background, in: RoundedRectangle(cornerRadius: theme.cardRadius))
                .environment(\.locale, options.locale ?? inheritedLocale)
                .environment(\.colorScheme, options.scheme ?? inheritedScheme)
        }
        .frame(maxWidth: .infinity)
    }

    private var theme: EControlTheme {
        var theme = inheritedTheme
        if options.largeText {
            theme.typography.nativeBodySize *= 1.35
            theme.typography.body = .system(size: theme.typography.nativeBodySize)
            theme.typography.secondary = .body
            theme.typography.caption = .callout
            theme.typography.monospaced = .system(size: theme.typography.nativeBodySize).monospaced()
            theme.typography.sectionTitle = .title2
            theme.typography.title = .title
        }
        return theme
    }

    private var placement: EControlPlacement { options.controlPlacement ?? inheritedPlacement }

}

/// 独立 NSHostingView 让原生 AppKit 字段和动态 NSColor 也采用局部外观；禁止改祖先窗口。
private struct ELocalPreviewHost<Content: View>: NSViewRepresentable {
    let scheme: ColorScheme?
    let increasedContrast: Bool
    let content: Content

    init(scheme: ColorScheme?, increasedContrast: Bool, @ViewBuilder content: () -> Content) {
        self.scheme = scheme
        self.increasedContrast = increasedContrast
        self.content = content()
    }

    func makeNSView(context: Context) -> NSHostingView<EPreviewRoot<Content>> {
        let view = NSHostingView(rootView: EPreviewRoot(content: content))
        view.sizingOptions = [.intrinsicContentSize]
        return view
    }

    func updateNSView(_ view: NSHostingView<EPreviewRoot<Content>>, context: Context) {
        view.rootView = EPreviewRoot(content: content, width: view.rootView.width)
        if let scheme {
            let name: NSAppearance.Name = increasedContrast
                ? (scheme == .dark ? .accessibilityHighContrastDarkAqua : .accessibilityHighContrastAqua)
                : (scheme == .dark ? .darkAqua : .aqua)
            view.appearance = NSAppearance(named: name)
        } else {
            view.appearance = nil
        }
    }

    func sizeThatFits(_ proposal: ProposedViewSize, nsView: NSHostingView<EPreviewRoot<Content>>, context: Context) -> CGSize? {
        let width = proposal.width ?? 500
        if nsView.rootView.width != width { nsView.rootView = EPreviewRoot(content: content, width: width) }
        return CGSize(width: width, height: nsView.fittingSize.height)
    }
}

private struct EPreviewRoot<Content: View>: View {
    let content: Content
    var width: CGFloat?
    var body: some View { content.frame(width: width, alignment: .leading) }
}
#endif
