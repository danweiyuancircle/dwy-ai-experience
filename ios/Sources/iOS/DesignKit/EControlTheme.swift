#if os(iOS)
import SwiftUI
import UIKit

/// 产品可替换的强调色对。四种环境均须提供匹配前景，正文和危险色不随品牌改变。
public struct EAccentColors: Sendable {
    public let light: Color
    public let onLight: Color
    public let dark: Color
    public let onDark: Color
    public let highContrastLight: Color
    public let onHighContrastLight: Color
    public let highContrastDark: Color
    public let onHighContrastDark: Color

    public init(
        light: Color, onLight: Color, dark: Color, onDark: Color,
        highContrastLight: Color, onHighContrastLight: Color,
        highContrastDark: Color, onHighContrastDark: Color
    ) {
        self.light = light
        self.onLight = onLight
        self.dark = dark
        self.onDark = onDark
        self.highContrastLight = highContrastLight
        self.onHighContrastLight = onHighContrastLight
        self.highContrastDark = highContrastDark
        self.onHighContrastDark = onHighContrastDark
    }

    /// 默认中性主题的蓝色强调，不表示整套材质已经完成对比验收。
    public static let standard = Self(
        light: Color(red: 37 / 255, green: 99 / 255, blue: 235 / 255), onLight: .white,
        dark: Color(red: 59 / 255, green: 130 / 255, blue: 246 / 255),
        onDark: Color(red: 10 / 255, green: 26 / 255, blue: 51 / 255),
        highContrastLight: Color(red: 30 / 255, green: 64 / 255, blue: 175 / 255),
        onHighContrastLight: .white,
        highContrastDark: Color(red: 147 / 255, green: 197 / 255, blue: 253 / 255),
        onHighContrastDark: Color(red: 10 / 255, green: 26 / 255, blue: 51 / 255)
    )
}

/// 本端唯一默认设计来源；仅包含值，不持有任务、服务、回调或持久化偏好。
public struct EControlTheme: Sendable {
    public var accent: EAccentColors
    public let colors = Colors()
    public let typography = Typography()
    public let spacing = Spacing()
    public let size = Size()
    public let radius = Radius()

    public init(accent: EAccentColors = .standard) {
        self.accent = accent
    }

    public static let standard = Self()

    /// 根据系统外观和增加对比度解析品牌；不改变系统文本及状态色。
    public func accentPair(scheme: ColorScheme, contrast: ColorSchemeContrast) -> (accent: Color, foreground: Color) {
        switch (scheme, contrast) {
        case (.dark, .increased): (accent.highContrastDark, accent.onHighContrastDark)
        case (.dark, _): (accent.dark, accent.onDark)
        case (_, .increased): (accent.highContrastLight, accent.onHighContrastLight)
        default: (accent.light, accent.onLight)
        }
    }

    /// 自绘边线使用一个物理像素；系统控件的边线由系统负责。
    public func hairline(displayScale: CGFloat) -> CGFloat { 1 / displayScale }

    /// UIKit 动态语义映射，随系统外观及辅助功能变化。
    public struct Colors: Sendable {
        public let background = Color(uiColor: .systemGroupedBackground)
        public let surface = Color(uiColor: .secondarySystemGroupedBackground)
        public let elevatedSurface = Color(uiColor: .tertiarySystemGroupedBackground)
        public let primary = Color.primary
        public let secondary = Color.secondary
        public let separator = Color(uiColor: .separator)
        public let success = Color(uiColor: .systemGreen)
        public let warning = Color(uiColor: .systemOrange)
        public let danger = Color(uiColor: .systemRed)
        public let selection = Color(uiColor: .tertiarySystemFill)
    }

    /// 语义字体保留 Dynamic Type，不暴露另一份固定字号表。
    public struct Typography: Sendable {
        public let title = Font.title2
        public let sectionTitle = Font.headline
        public let body = Font.body
        public let secondary = Font.subheadline
        public let caption = Font.caption
        public let monospaced = Font.body.monospaced()
    }

    /// 用于平台组件内部的标准间距；产品不逐页重填像素。
    public struct Spacing: Sendable {
        public let inline: CGFloat = 4
        public let controlGroup: CGFloat = 8
        public let fieldLabel: CGFloat = 6
        public let formRow: CGFloat = 12
        public let group: CGFloat = 16
        public let section: CGFloat = 24
        public let cardInset: CGFloat = 16
        public func pageInset(horizontalSizeClass: UserInterfaceSizeClass?) -> CGFloat {
            horizontalSizeClass == .regular ? 24 : 16
        }
    }

    /// 外壳/触点下限，内容和辅助字号可继续撑高。
    public struct Size: Sendable {
        public let iconGlyph: CGFloat = 20
        public let iconHit: CGFloat = 44
        public let action: CGFloat = 44
        public let field: CGFloat = 44
        public let search: CGFloat = 44
        public let row: CGFloat = 44
        public let toolbarAction: CGFloat = 44
    }

    /// 仅用于自绘字段与内容卡；原生按钮与呈现圆角不覆盖。
    public struct Radius: Sendable {
        public let field: CGFloat = 12
        public let card: CGFloat = 16
        public let group: CGFloat = 16
    }
}

/// 仅浮动操作在 iOS 26 使用原生玻璃；普通内容保留标准控件样式。
public enum EControlPlacement: Sendable {
    case content
    case navigation
    case floating
}

private struct EControlThemeKey: EnvironmentKey {
    static let defaultValue = EControlTheme.standard
}

private struct EControlPlacementKey: EnvironmentKey {
    static let defaultValue = EControlPlacement.content
}

public extension EnvironmentValues {
    var eControlTheme: EControlTheme {
        get { self[EControlThemeKey.self] }
        set { self[EControlThemeKey.self] = newValue }
    }

    var eControlPlacement: EControlPlacement {
        get { self[EControlPlacementKey.self] }
        set { self[EControlPlacementKey.self] = newValue }
    }
}

public extension View {
    /// 对当前 scene/子树注入值主题，不申请权限或写入用户偏好。
    func eControlTheme(_ theme: EControlTheme) -> some View {
        environment(\.eControlTheme, theme)
    }

    /// 明确材质场景；不改变系统导航或弹层的所有权。
    func eControlPlacement(_ placement: EControlPlacement) -> some View {
        environment(\.eControlPlacement, placement)
    }
}

#endif
