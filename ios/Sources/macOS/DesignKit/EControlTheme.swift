#if os(macOS)
import SwiftUI
import AppKit

/// Mac 语义颜色。系统文本、危险色与焦点不随品牌替换；强调色需和 onAccent 一起验证。
public struct ESemanticColors: Sendable {
    public var background = Color(nsColor: .windowBackgroundColor)
    public var surface = Color(nsColor: .controlBackgroundColor)
    public var elevatedSurface = Color(nsColor: .controlBackgroundColor)
    public var text = Color.primary
    public var secondaryText = Color.secondary
    public var separator = Color(nsColor: .separatorColor)
    public var accent = Self.defaultAccent
    public var onAccent = Self.defaultOnAccent
    public var success = Color(nsColor: .systemGreen)
    public var warning = Color(nsColor: .systemOrange)
    public var danger = Color(nsColor: .systemRed)
    public var selection = Color(nsColor: .selectedContentBackgroundColor)

    /// 标准中性与蓝色主题，动态跟随系统外观与增加对比度。
    public init() {}

    private static let defaultAccent = brand(light: 0x2563EB, dark: 0x3B82F6, highLight: 0x1E40AF, highDark: 0x93C5FD)
    private static let defaultOnAccent = brand(light: 0xFFFFFF, dark: 0x0A1A33, highLight: 0xFFFFFF, highDark: 0x0A1A33)

    private static func brand(light: UInt32, dark: UInt32, highLight: UInt32, highDark: UInt32) -> Color {
        Color(nsColor: NSColor(name: nil) { appearance in
            let match = appearance.bestMatch(from: [.aqua, .darkAqua, .accessibilityHighContrastAqua, .accessibilityHighContrastDarkAqua])
            let value: UInt32
            switch match {
            case .darkAqua: value = dark
            case .accessibilityHighContrastAqua: value = highLight
            case .accessibilityHighContrastDarkAqua: value = highDark
            default: value = light
            }
            return NSColor(srgbRed: Double((value >> 16) & 255) / 255,
                           green: Double((value >> 8) & 255) / 255,
                           blue: Double(value & 255) / 255, alpha: 1)
        })
    }
}

/// 语义字体保留系统缩放和语言字形布局，不复制系统字号表。
public struct ETypography: Sendable {
    /// AppKit 编辑器的原生正文字号；SwiftUI Font 不可反向转换，产品字号根映射须同步设置此值。
    public var nativeBodySize: CGFloat = NSFont.preferredFont(forTextStyle: .body).pointSize
    public var title: Font = .title3
    public var sectionTitle: Font = .headline
    public var body: Font = .body
    public var secondary: Font = .callout
    public var caption: Font = .caption
    public var monospaced: Font = .body.monospaced()
    public init() {}
}

/// Mac 标准密度的离散间距；业务页面引用角色而非复制数值。
public struct ESpacing: Sendable {
    public var inline: CGFloat = 4
    public var controlGroup: CGFloat = 8
    public var fieldLabel: CGFloat = 6
    public var formRow: CGFloat = 8
    public var group: CGFloat = 12
    public var section: CGFloat = 20
    public var pageInset: CGFloat = 20
    public var cardInset: CGFloat = 12
    public init() {}
}

/// Mac 控件主题是稳定的值配置，不持有服务、业务状态或回调。
public struct EControlTheme: Sendable {
    /// Environment 复用同一个值，避免默认读取时重复创建动态颜色提供器。
    public static let standard = EControlTheme()
    public var colors = ESemanticColors()
    public var typography = ETypography()
    public var spacing = ESpacing()
    public var accent: Color {
        get { colors.accent }
        set { colors.accent = newValue }
    }
    public var fieldHeight: CGFloat
    public var searchHeight: CGFloat
    public var iconSide: CGFloat
    public var chromeIconSide: CGFloat
    public var fieldRadius: CGFloat
    public var cardRadius: CGFloat = 8
    public var iconGlyph: CGFloat = 13
    public var toolbarGlyph: CGFloat = 16

    /// 默认开箱可用；自定义品牌时同时设置 colors.onAccent，验证明暗与高对比组合。
    public init(accent: Color = ESemanticColors().accent, fieldHeight: CGFloat = 28,
                searchHeight: CGFloat = 36, iconSide: CGFloat = 28,
                chromeIconSide: CGFloat = 34, fieldRadius: CGFloat = 8) {
        self.colors.accent = accent
        self.fieldHeight = fieldHeight
        self.searchHeight = searchHeight
        self.iconSide = iconSide
        self.chromeIconSide = chromeIconSide
        self.fieldRadius = fieldRadius
    }
}

/// 材质按层级选择，系统工具栏不重复绘制玻璃背景。
public enum EControlPlacement: Sendable { case content, floating, toolbar }

extension EnvironmentValues {
    @Entry public var eControlTheme = EControlTheme.standard
    @Entry public var eControlPlacement: EControlPlacement = .content
}

extension View {
    /// 每个独立 scene/NSHostingView 根单独装配主题，不推断另一窗口的环境。
    public func eControlTheme(_ theme: EControlTheme) -> some View {
        environment(\.eControlTheme, theme).tint(theme.accent)
    }

    /// 只声明操作区域，不改变窗口、导航和业务路由。
    public func eControlPlacement(_ placement: EControlPlacement) -> some View {
        environment(\.eControlPlacement, placement)
    }
}

struct EFieldChrome: ViewModifier {
    @Environment(\.eControlTheme) private var theme
    @Environment(\.displayScale) private var displayScale
    var isSearch = false

    func body(content: Content) -> some View {
        content
            .padding(.horizontal, theme.spacing.controlGroup)
            .frame(minHeight: isSearch ? theme.searchHeight : theme.fieldHeight)
            .background(theme.colors.surface, in: RoundedRectangle(cornerRadius: theme.fieldRadius))
            .overlay {
                RoundedRectangle(cornerRadius: theme.fieldRadius)
                    .strokeBorder(theme.colors.separator, lineWidth: 1 / displayScale)
            }
    }
}
#endif
