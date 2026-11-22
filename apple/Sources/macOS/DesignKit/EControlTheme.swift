#if os(macOS)
import SwiftUI
import AppKit

/// Mac 内容区的明暗配色。原生窗口材质、选中态和焦点由系统控件处理。
public struct ESemanticColors: Sendable {
    public var background: Color
    public var surface: Color
    public var elevatedSurface: Color
    public var text: Color
    public var secondaryText: Color
    public var tertiaryText: Color
    public var canvas: Color
    public var sidebarSurface = Color.primary.opacity(0.025)
    /// 默认跟随当前主题的强调色，应用可单独覆盖悬停底色。
    public var hover: Color {
        get { hoverOverride ?? accent.opacity(0.07) }
        set { hoverOverride = newValue }
    }
    public var separator: Color
    public var accent: Color
    public var onAccent: Color
    public var success: Color
    public var warning: Color
    public var danger: Color
    public var selection = Color(nsColor: .selectedContentBackgroundColor)

    private var hoverOverride: Color?
    private static let standard = ESemanticColors(appearance: nil)

    /// 标准灰阶与冷静蓝，随系统明暗和增加对比度设置解析。
    public init() { self = Self.standard }

    // AppKit 按系统设置选择有效外观，传入名称可独立检验各套色值。
    init(appearance: NSAppearance.Name?) {
        func adaptive(light: UInt32, dark: UInt32, highLight: UInt32? = nil, highDark: UInt32? = nil) -> Color {
            @Sendable func color(_ name: NSAppearance.Name) -> NSColor {
                let value: UInt32
                switch name {
                case .darkAqua, .vibrantDark: value = dark
                case .accessibilityHighContrastAqua, .accessibilityHighContrastVibrantLight: value = highLight ?? light
                case .accessibilityHighContrastDarkAqua, .accessibilityHighContrastVibrantDark: value = highDark ?? dark
                default: value = light
                }
                return NSColor(srgbRed: Double((value >> 16) & 255) / 255,
                               green: Double((value >> 8) & 255) / 255,
                               blue: Double(value & 255) / 255, alpha: 1)
            }

            if let appearance { return Color(nsColor: color(appearance)) }
            return Color(nsColor: NSColor(name: nil) { color($0.name) })
        }

        background = adaptive(light: 0xFAFAFA, dark: 0x0A0A0B)
        surface = adaptive(light: 0xFFFFFF, dark: 0x18181B)
        elevatedSurface = adaptive(light: 0xFFFFFF, dark: 0x1F1F23)
        text = adaptive(light: 0x18181B, dark: 0xF4F4F5)
        secondaryText = adaptive(light: 0x6B6B74, dark: 0x8E8E96, highLight: 0x52525B, highDark: 0xB4B4BE)
        // 两个说明文字角色都可能用于读写任务，沿用满足对比度的灰色。
        tertiaryText = secondaryText
        canvas = adaptive(light: 0xF4F4F5, dark: 0x111113)
        separator = adaptive(light: 0xEBEBEB, dark: 0x2A2A2D, highLight: 0x71717A, highDark: 0xA1A1AA)
        accent = adaptive(light: 0x2563EB, dark: 0x3B82F6, highLight: 0x1E40AF, highDark: 0x93C5FD)
        onAccent = adaptive(light: 0xFFFFFF, dark: 0x0A1A33)
        success = adaptive(light: 0x047857, dark: 0x4ADE80, highLight: 0x064E3B, highDark: 0x86EFAC)
        warning = adaptive(light: 0xC2410C, dark: 0xFB923C, highLight: 0x7C2D12, highDark: 0xFDBA74)
        danger = adaptive(light: 0xB91C1C, dark: 0xFB7185, highLight: 0x991B1B, highDark: 0xFDA4AF)
    }
}

/// Mac 内容字体角色。默认正文 13 pt，SwiftUI 和原生编辑器共用正文字号。
public struct ETypography: Sendable {
    /// AppKit 编辑器使用的正文字号。应用单独改 `body` 时应同步此值。
    public var nativeBodySize: CGFloat
    public var title: Font
    public var pageTitle: Font = .title2.bold()
    public var sectionTitle: Font
    public var body: Font
    public var secondary: Font
    public var caption: Font
    public var monospaced: Font

    /// 使用标准字号初始化各字体角色。
    public init() { self.init(bodySize: 13) }

    /// 传入大于 2 pt 的正文字号，同时配置 SwiftUI 字体和原生编辑器。页面标题沿用系统样式。
    public init(bodySize: CGFloat) {
        nativeBodySize = bodySize
        title = .system(size: bodySize + 5, weight: .semibold)
        sectionTitle = .system(size: bodySize, weight: .semibold)
        body = .system(size: bodySize)
        secondary = .system(size: bodySize - 2)
        caption = secondary
        monospaced = .system(size: bodySize, design: .monospaced)
    }
}

/// 标准页面语义间距；旧消费方可通过类型别名接入，不再复制数字表。
public enum ESpace {
    public static var list: CGFloat { EControlTheme.standard.spacing.inline / 2 }
    public static var xs: CGFloat { EControlTheme.standard.spacing.inline }
    public static var s: CGFloat { EControlTheme.standard.spacing.fieldLabel }
    public static var title: CGFloat { EControlTheme.standard.spacing.controlGroup }
    public static var tight: CGFloat { EControlTheme.standard.spacing.controlGroup }
    public static var inset: CGFloat { EControlTheme.standard.spacing.group }
    public static var row: CGFloat { EControlTheme.standard.spacing.group }
    public static var rowInner: CGFloat { EControlTheme.standard.spacing.group }
    public static var section: CGFloat { EControlTheme.standard.spacing.section }
    public static var xl: CGFloat { EControlTheme.standard.spacing.pageInset }
    public static var chrome: CGFloat { EControlTheme.standard.spacing.pageInset }
    public static var page: CGFloat { EControlTheme.standard.spacing.pageInset }
    public static var hero: CGFloat { EControlTheme.standard.fieldHeight }
    public static var empty: CGFloat { EControlTheme.standard.spacing.pageInset * 2 }
}

/// 标准页面圆角与控件主题共源；产品不再单独维护通用半径。
public enum ERadius {
    public static var badge: CGFloat { EControlTheme.standard.fieldRadius / 2 }
    public static var menu: CGFloat { EControlTheme.standard.fieldRadius / 2 }
    public static var control: CGFloat { EControlTheme.standard.fieldRadius }
    public static var row: CGFloat { EControlTheme.standard.fieldRadius }
    public static var card: CGFloat { EControlTheme.standard.cardRadius }
    public static var tile: CGFloat { EControlTheme.standard.cardRadius }
    public static var panel: CGFloat { EControlTheme.standard.cardRadius }
    public static var overlay: CGFloat { EControlTheme.standard.cardRadius * 2 }
}

/// 标准页面字体，正文、标题与辅助内容沿用共享主题的语义角色。
public enum ETypeScale {
    public static var pageTitle: Font { EControlTheme.standard.typography.pageTitle }
    public static var detail: Font { EControlTheme.standard.typography.secondary }
    public static var bodyPoint: CGFloat { EControlTheme.standard.typography.nativeBodySize }
    public static var body: Font { EControlTheme.standard.typography.body }
    public static var control: Font { body.weight(.medium) }
    public static var rowTitle: Font { body }
    public static var metaPoint: CGFloat { NSFont.preferredFont(forTextStyle: .caption1).pointSize }
    public static var meta: Font { EControlTheme.standard.typography.caption }
    public static var metaStrong: Font { meta.weight(.medium) }
    public static var badge: Font { meta.weight(.medium) }
    public static var badgeStrong: Font { meta.weight(.semibold) }
    public static var iconDrag: Font { meta }
    public static var iconMenu: Font { body }
    public static var iconAction: Font { EControlTheme.standard.typography.title }
    public static var iconRow: Font { body }
    public static var iconHero: Font { .largeTitle }
    public static var iconWelcome: Font { .largeTitle }
    public static var iconUnlock: Font { .largeTitle }
    public static var monoBody: Font { EControlTheme.standard.typography.monospaced }
    public static var monoCaption: Font { meta.monospaced() }
    public static var monoCaption2: Font { meta.monospaced() }
    public static func sidebar(selected: Bool) -> Font { body.weight(selected ? .semibold : .regular) }
}

/// 标准语义表面和叠色。产品品牌可配置主题，通用视觉档位只在基础库定义。
public enum EPalette {
    private static var colors: ESemanticColors { EControlTheme.standard.colors }
    public static var accent: Color { colors.accent }
    public static var label: Color { colors.text }
    public static var secondaryLabel: Color { colors.secondaryText }
    public static var tertiaryLabel: Color { colors.tertiaryText }
    public static var onAccent: Color { colors.onAccent }
    public static var danger: Color { colors.danger }
    public static var warning: Color { colors.warning }
    public static var success: Color { colors.success }
    public static var window: Color { colors.background }
    public static var canvas: Color { colors.canvas }
    public static var row: Color { colors.surface }
    public static var separator: Color { colors.separator }
    public static var sidebarShade: Color { colors.sidebarSurface }
    public enum AccentWash { case column, hover, banner, selected, badge, glow }
    public static func accent(_ wash: AccentWash) -> Color {
        switch wash {
        case .column: accent.opacity(0.08)
        case .hover: colors.hover
        case .banner: accent.opacity(0.12)
        case .selected: colors.selection
        case .badge: accent.opacity(0.2)
        case .glow: accent.opacity(0.25)
        }
    }
    public enum InkWash { case card, hairline, stroke }
    public static func ink(_ wash: InkWash) -> Color {
        switch wash {
        case .card: colors.text.opacity(0.06)
        case .hairline: colors.text.opacity(0.08)
        case .stroke: colors.text.opacity(0.12)
        }
    }
    public static var warningFill: Color { colors.warning.opacity(0.2) }
    public static var warningBanner: Color { colors.warning.opacity(0.14) }
    public static var successFill: Color { colors.success.opacity(0.12) }
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
