#if os(macOS)
import SwiftUI

/// 设置和工具页共用页头；文案由宿主解析，长标题不固定行高。
public struct EPageHeader: View {
    @Environment(\.eControlTheme) private var theme
    private let title: Text
    private let subtitle: Text?

    public init(title: Text, subtitle: Text? = nil) {
        self.title = title
        self.subtitle = subtitle
    }

    public var body: some View {
        VStack(alignment: .leading, spacing: theme.spacing.fieldLabel) {
            title.font(theme.typography.pageTitle).foregroundStyle(theme.colors.text)
            if let subtitle {
                subtitle.font(theme.typography.secondary).foregroundStyle(theme.colors.secondaryText)
                    .fixedSize(horizontal: false, vertical: true)
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
    }
}

/// 设置页的滚动、留白与阅读宽度统一入口；业务方只提供正文。
public struct ESettingsPage<Content: View>: View {
    @Environment(\.eControlTheme) private var theme
    private let maxContentWidth: CGFloat?
    private let content: Content

    public init(maxContentWidth: CGFloat? = nil, @ViewBuilder content: () -> Content) {
        self.maxContentWidth = maxContentWidth
        self.content = content()
    }

    public var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: theme.spacing.section) { content }
                .frame(maxWidth: maxContentWidth, alignment: .leading)
                .padding(theme.spacing.pageInset)
                .frame(maxWidth: .infinity, alignment: .leading)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .topLeading)
        .background(theme.colors.background)
    }
}

/// 多操作设置行外壳；不合并内部焦点，排序与业务动作仍由宿主处理。
public struct EItemRow<Content: View>: View {
    @Environment(\.eControlTheme) private var theme
    @State private var hovered = false
    private let isSelected: Bool
    private let content: Content

    public init(isSelected: Bool = false, @ViewBuilder content: () -> Content) {
        self.isSelected = isSelected
        self.content = content()
    }

    public var body: some View {
        HStack(spacing: theme.spacing.group) { content }
            .padding(.horizontal, theme.spacing.group)
            .padding(.vertical, theme.spacing.inline)
            .frame(maxWidth: .infinity, minHeight: theme.fieldHeight)
            .background(isSelected || hovered ? theme.colors.hover : .clear,
                        in: RoundedRectangle(cornerRadius: theme.fieldRadius))
            .contentShape(Rectangle())
            .onHover { hovered = $0 }
            .accessibilityElement(children: .contain)
    }
}

/// 侧栏项只提供统一文字、图标及密度；原生 List 仍拥有选择与键盘导航。
public struct ESidebarItem<Content: View>: View {
    @Environment(\.eControlTheme) private var theme
    private let content: Content

    public init(@ViewBuilder content: () -> Content) { self.content = content() }

    public var body: some View {
        content.font(theme.typography.body)
            .frame(maxWidth: .infinity, minHeight: theme.fieldHeight, alignment: .leading)
            .padding(.vertical, theme.spacing.inline)
    }
}

/// 紧凑管理列表的原生平台样式，业务方不再重复指定控件外观。
public struct EManagementListStyle: ViewModifier {
    public init() {}
    public func body(content: Content) -> some View {
        content.listStyle(.plain).scrollContentBackground(.hidden)
            .toggleStyle(.switch).controlSize(.small).buttonStyle(.borderless)
    }
}

/// 工具任务进度与取消区的通用布局；动作只请求取消，任务生命周期由宿主管理。
public struct EProgressPanelContent<Actions: View>: View {
    @Environment(\.eControlTheme) private var theme
    private let title: Text
    private let fraction: EProgressFraction?
    private let hint: Text?
    private let actions: Actions

    public init(title: Text, fraction: EProgressFraction? = nil, hint: Text? = nil,
                @ViewBuilder actions: () -> Actions) {
        self.title = title
        self.fraction = fraction
        self.hint = hint
        self.actions = actions()
    }

    public var body: some View {
        VStack(alignment: .leading, spacing: theme.spacing.group) {
            ETaskProgress(title, fraction: fraction) { EmptyView() }
                .lineLimit(2).truncationMode(.middle)
                .help(title)
            if let hint {
                hint.font(theme.typography.secondary).foregroundStyle(theme.colors.secondaryText)
                    .fixedSize(horizontal: false, vertical: true)
            }
            HStack { Spacer(minLength: 0); actions }
        }
        .padding(theme.spacing.pageInset)
        .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .topLeading)
    }
}
#endif
