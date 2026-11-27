#if os(macOS)
import SwiftUI

/// 文本语义角色。字体读 `ETypography`，颜色读 `ESemanticColors`，业务页面用它代替
/// `.font(.caption)`、`.foregroundStyle(.secondary)` 这类系统字体与系统色的裸写。
public enum ETextRole: Sendable, CaseIterable {
    /// 正文。
    case body
    /// 次要说明，使用次要文字色。
    case secondary
    /// 脚注、标签与状态说明，使用次要文字色。
    case caption
    /// 卡片或区块标题。
    case title
    /// 设置分组标题。
    case sectionTitle
    /// 页面标题。
    case pageTitle
    /// 等宽文本，用于路径、序列号、日志等。
    case monospaced

    func font(_ typography: ETypography) -> Font {
        switch self {
        case .body: typography.body
        case .secondary: typography.secondary
        case .caption: typography.caption
        case .title: typography.title
        case .sectionTitle: typography.sectionTitle
        case .pageTitle: typography.pageTitle
        case .monospaced: typography.monospaced
        }
    }

    /// `tone` 为空或 `.neutral` 时保持角色自身的颜色；其余语义色覆盖角色颜色。
    func color(_ colors: ESemanticColors, tone: EStatusTone? = nil) -> Color {
        if let tone, tone != .neutral { return tone.color(colors) }
        switch self {
        case .secondary, .caption: return colors.secondaryText
        case .body, .title, .sectionTitle, .pageTitle, .monospaced: return colors.text
        }
    }
}

private struct ETextStyle: ViewModifier {
    @Environment(\.eControlTheme) private var theme
    let role: ETextRole
    let tone: EStatusTone?

    func body(content: Content) -> some View {
        content
            .font(role.font(theme.typography))
            .foregroundStyle(role.color(theme.colors, tone: tone))
    }
}

extension View {
    /// 把文本角色套在任意视图上（`Text`、`Label` 等）。需要颜色语义时传 `tone`，
    /// 状态仍须配有可读文字，不能只靠颜色区分。主题来自 `.eControlTheme(_:)` 注入的环境。
    public func eText(_ role: ETextRole = .body, tone: EStatusTone? = nil) -> some View {
        modifier(ETextStyle(role: role, tone: tone))
    }
}

/// 带主题角色的文本。文案由宿主显式传入，基础库不引用应用本地化 key 或资源。
/// 需要 `lineLimit`、`textSelection` 等修饰时照常链式调用。
public struct EText: View {
    private let text: Text
    private let role: ETextRole
    private let tone: EStatusTone?

    /// 已解析应用文案或格式化文本通过 `Text` 保留其本地化语义。
    public init(_ text: Text, role: ETextRole = .body, tone: EStatusTone? = nil) {
        self.text = text
        self.role = role
        self.tone = tone
    }

    public init(_ resource: LocalizedStringResource, role: ETextRole = .body, tone: EStatusTone? = nil) {
        self.init(Text(resource), role: role, tone: tone)
    }

    /// 原文不走本地化，用于设备名、路径等运行时数据。
    public init(verbatim content: String, role: ETextRole = .body, tone: EStatusTone? = nil) {
        self.init(Text(verbatim: content), role: role, tone: tone)
    }

    public var body: some View {
        text.eText(role, tone: tone)
    }
}
#endif
