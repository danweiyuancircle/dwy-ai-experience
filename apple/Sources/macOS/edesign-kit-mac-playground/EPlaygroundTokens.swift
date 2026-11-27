#if os(macOS)
import SwiftUI
import AppKit
import DesignKitMac

/// 主题与设计令牌的数据来源。所有数值从传入的 `EControlTheme` 读取，页面不复制数字表，
/// 主题改动后展示与测试同步变化。
enum EPlaygroundTokens {
    struct Metric: Identifiable {
        let name: String
        let value: CGFloat
        var id: String { name }
    }

    struct ColorToken: Identifiable {
        let name: String
        let color: Color
        var id: String { name }
    }

    static func colors(_ colors: ESemanticColors) -> [ColorToken] {
        [
            ColorToken(name: "background", color: colors.background),
            ColorToken(name: "surface", color: colors.surface),
            ColorToken(name: "elevatedSurface", color: colors.elevatedSurface),
            ColorToken(name: "canvas", color: colors.canvas),
            ColorToken(name: "sidebarSurface", color: colors.sidebarSurface),
            ColorToken(name: "text", color: colors.text),
            ColorToken(name: "secondaryText", color: colors.secondaryText),
            ColorToken(name: "tertiaryText", color: colors.tertiaryText),
            ColorToken(name: "separator", color: colors.separator),
            ColorToken(name: "accent", color: colors.accent),
            ColorToken(name: "onAccent", color: colors.onAccent),
            ColorToken(name: "hover", color: colors.hover),
            ColorToken(name: "selection", color: colors.selection),
            ColorToken(name: "success", color: colors.success),
            ColorToken(name: "warning", color: colors.warning),
            ColorToken(name: "danger", color: colors.danger),
        ]
    }

    static func spacing(_ theme: EControlTheme) -> [Metric] {
        let spacing = theme.spacing
        return [
            Metric(name: "inline", value: spacing.inline),
            Metric(name: "fieldLabel", value: spacing.fieldLabel),
            Metric(name: "controlGroup", value: spacing.controlGroup),
            Metric(name: "formRow", value: spacing.formRow),
            Metric(name: "group", value: spacing.group),
            Metric(name: "cardInset", value: spacing.cardInset),
            Metric(name: "section", value: spacing.section),
            Metric(name: "pageInset", value: spacing.pageInset),
        ]
    }

    static func radii(_ theme: EControlTheme) -> [Metric] {
        [Metric(name: "fieldRadius", value: theme.fieldRadius), Metric(name: "cardRadius", value: theme.cardRadius)]
    }

    static func controlSizes(_ theme: EControlTheme) -> [Metric] {
        [
            Metric(name: "fieldHeight", value: theme.fieldHeight),
            Metric(name: "searchHeight", value: theme.searchHeight),
            Metric(name: "iconSide", value: theme.iconSide),
            Metric(name: "chromeIconSide", value: theme.chromeIconSide),
            Metric(name: "iconGlyph", value: theme.iconGlyph),
            Metric(name: "toolbarGlyph", value: theme.toolbarGlyph),
        ]
    }

    /// 动态色必须在目标外观下解析，否则两列色值都会读到当前窗口外观；半透明令牌追加透明度。
    static func hex(_ color: Color, scheme: ColorScheme) -> String {
        var result = "-"
        NSAppearance(named: scheme == .dark ? .darkAqua : .aqua)?.performAsCurrentDrawingAppearance {
            guard let resolved = NSColor(color).usingColorSpace(.sRGB) else { return }
            func byte(_ value: CGFloat) -> Int { Int((value * 255).rounded()) }
            result = String(format: "#%02X%02X%02X", byte(resolved.redComponent), byte(resolved.greenComponent), byte(resolved.blueComponent))
            if resolved.alphaComponent < 0.995 { result += " \(Int((resolved.alphaComponent * 100).rounded()))%" }
        }
        return result
    }
}

/// 启动参数让截图和文档链接能直达页面、外观、语言与示例状态；非法值回退为默认，不影响正常启动。
struct EPlaygroundLaunch {
    var component: EPlaygroundComponent?
    var showsTokens = false
    var options = EPreviewOptions()
    var scenario = EPlaygroundScenario.normal

    static let current = EPlaygroundLaunch(arguments: ProcessInfo.processInfo.arguments)

    init(arguments: [String]) {
        func value(after flag: String) -> String? {
            guard let index = arguments.firstIndex(of: flag), arguments.indices.contains(index + 1) else { return nil }
            return arguments[index + 1]
        }
        if let page = value(after: "--page") {
            showsTokens = page == "tokens"
            component = EPlaygroundComponent.allCases.first { $0.id == page || $0.rawValue == page }
        }
        switch value(after: "--appearance") {
        case "light": options.appearance = 1
        case "dark": options.appearance = 2
        default: break
        }
        switch value(after: "--language") {
        case "en": options.language = 1
        case "zh-Hans": options.language = 2
        default: break
        }
        if let name = value(after: "--scenario"), let parsed = EPlaygroundScenario(rawValue: name) { scenario = parsed }
    }
}

struct EPlaygroundTokensDetail: View {
    let options: EPreviewOptions

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                Text("Theme and tokens", bundle: .module).font(.title2).accessibilityAddTraits(.isHeader)
                Text(verbatim: "EControlTheme · DesignKitMac · macOS 26.0").font(.caption).foregroundStyle(.secondary)
                Text("Values are read from the injected EControlTheme; light and dark follow the preview appearance setting", bundle: .module)
                    .foregroundStyle(.secondary)
                EPreviewArea(options: options) { TokenSheet() }
            }
            .padding(20)
            .frame(maxWidth: .infinity, alignment: .leading)
        }
        .accessibilityIdentifier("playground.tokens.page")
    }
}

private struct TokenSheet: View {
    @Environment(\.eControlTheme) private var theme

    var body: some View {
        VStack(alignment: .leading, spacing: ESpace.section) {
            section("Colors") { colorTable }
            section("Typography") {
                ForEach(ETextRole.allCases, id: \.self) { role in
                    HStack(alignment: .firstTextBaseline) {
                        EText(verbatim: "\(role)", role: .monospaced).frame(width: 130, alignment: .leading)
                        EText(verbatim: "The quick brown fox 敏捷的棕色狐狸", role: role)
                    }
                }
                EText(verbatim: "nativeBodySize \(Int(theme.typography.nativeBodySize)) pt", role: .caption)
            }
            section("Spacing") {
                ForEach(EPlaygroundTokens.spacing(theme)) { token in
                    HStack {
                        EText(verbatim: token.name, role: .monospaced).frame(width: 130, alignment: .leading)
                        RoundedRectangle(cornerRadius: 2).fill(theme.colors.accent).frame(width: token.value, height: 12)
                        EText(verbatim: "\(Int(token.value)) pt", role: .caption)
                    }
                }
            }
            section("Corner radius") {
                HStack(spacing: ESpace.section) {
                    ForEach(EPlaygroundTokens.radii(theme)) { token in
                        VStack(spacing: ESpace.xs) {
                            RoundedRectangle(cornerRadius: token.value)
                                .strokeBorder(theme.colors.accent, lineWidth: 2).frame(width: 72, height: 48)
                            EText(verbatim: "\(token.name) \(Int(token.value))", role: .caption)
                        }
                    }
                }
            }
            section("Control sizes") {
                ForEach(EPlaygroundTokens.controlSizes(theme)) { token in
                    HStack {
                        EText(verbatim: token.name, role: .monospaced).frame(width: 130, alignment: .leading)
                        RoundedRectangle(cornerRadius: 4).fill(theme.colors.accent.opacity(0.35))
                            .frame(width: max(token.value, 4), height: max(token.value, 4))
                        EText(verbatim: "\(Int(token.value)) pt", role: .caption)
                    }
                }
            }
        }
    }

    private var colorTable: some View {
        VStack(alignment: .leading, spacing: ESpace.s) {
            HStack {
                Spacer().frame(width: 164 + ESpace.s)
                Text("Light", bundle: .module).eText(.caption).frame(width: 130, alignment: .leading)
                Text("Dark", bundle: .module).eText(.caption)
            }
            ForEach(EPlaygroundTokens.colors(theme.colors)) { token in
                HStack(spacing: ESpace.s) {
                    RoundedRectangle(cornerRadius: ERadius.badge).fill(token.color)
                        .overlay { RoundedRectangle(cornerRadius: ERadius.badge).strokeBorder(theme.colors.separator) }
                        .frame(width: 28, height: 20)
                        .accessibilityHidden(true)
                    EText(verbatim: token.name, role: .monospaced).frame(width: 130, alignment: .leading)
                    EText(verbatim: EPlaygroundTokens.hex(token.color, scheme: .light), role: .caption)
                        .frame(width: 130, alignment: .leading)
                    EText(verbatim: EPlaygroundTokens.hex(token.color, scheme: .dark), role: .caption)
                }
            }
        }
    }

    private func section<Content: View>(_ title: LocalizedStringKey, @ViewBuilder content: () -> Content) -> some View {
        VStack(alignment: .leading, spacing: ESpace.s) {
            Text(title, bundle: .module).eText(.sectionTitle)
            content()
        }
    }
}
#endif
