#if os(macOS)
import DesignKitMac
import SwiftUI

// 设置页的行级原件：带图标徽标的菜单、开关、只读、可点四种行，以及自动在行间画分隔线的分组卡片。
// 为什么集中在这里：多个应用的设置页交互必须一致，应用只提供标题、图标和数据，不再各自拼 HStack。

/// 行首图标徽标。尺寸固定，保证同一分组内标题左缘对齐，分隔线按它的宽度缩进。
struct BusinessSettingsIcon: View {
    static let side: CGFloat = 28
    @Environment(\.eControlTheme) private var theme
    let systemImage: String

    var body: some View {
        Image(systemName: systemImage)
            .font(theme.typography.sectionTitle)
            .foregroundStyle(theme.colors.accent)
            .frame(width: Self.side, height: Self.side)
            .background(RoundedRectangle(cornerRadius: 7).fill(theme.colors.accent.opacity(0.14)))
            .accessibilityHidden(true)
    }
}

/// 行的统一骨架：图标、标题与说明、尾部控件。
private struct BusinessSettingsRowLayout<Trailing: View>: View {
    @Environment(\.eControlTheme) private var theme
    let systemImage: String
    let title: Text
    let detail: Text?
    let verticalPadding: CGFloat
    let trailing: Trailing

    var body: some View {
        HStack(spacing: theme.spacing.group) {
            BusinessSettingsIcon(systemImage: systemImage)
            VStack(alignment: .leading, spacing: theme.spacing.inline) {
                title.font(theme.typography.body).foregroundStyle(theme.colors.text)
                if let detail {
                    detail.font(theme.typography.secondary).foregroundStyle(theme.colors.secondaryText)
                        .fixedSize(horizontal: false, vertical: true)
                }
            }
            Spacer(minLength: theme.spacing.inline)
            trailing
        }
        .padding(.horizontal, theme.spacing.group)
        .padding(.vertical, verticalPadding)
    }
}

/// 设置分组卡片。行之间自动加缩进分隔线，条件行不显示时不会留下多余分隔线。
/// 必须放进 `ECard` 之外的设置页内容中使用，卡片由本类型自带。
public struct BusinessSettingsGroup<Content: View>: View {
    @Environment(\.eControlTheme) private var theme
    private let content: Content

    public init(@ViewBuilder content: () -> Content) {
        self.content = content()
    }

    public var body: some View {
        ECard {
            VStack(spacing: 0) {
                // 用 subviews 遍历而不是手写 Divider：if / ForEach 产生的行数在运行时才确定。
                Group(subviews: content) { subviews in
                    ForEach(subviews.indices, id: \.self) { index in
                        if index > 0 {
                            Divider().padding(.leading, BusinessSettingsIcon.side + theme.spacing.group * 2)
                        }
                        subviews[index]
                    }
                }
            }
        }
    }
}

/// 只读信息行，右侧显示值，值可选中复制。
public struct BusinessInfoRow: View {
    private let systemImage: String
    private let title: Text
    private let value: Text
    @Environment(\.eControlTheme) private var theme

    public init(systemImage: String, title: Text, value: Text) {
        self.systemImage = systemImage
        self.title = title
        self.value = value
    }

    public var body: some View {
        BusinessSettingsRowLayout(
            systemImage: systemImage, title: title, detail: nil, verticalPadding: theme.spacing.formRow,
            trailing: value.font(theme.typography.body).foregroundStyle(theme.colors.secondaryText)
                .textSelection(.enabled)
        )
    }
}

/// 开关行。强制 `ESwitch` 的 switch 样式，避免 macOS 默认复选框；说明文案可选。
public struct BusinessToggleRow: View {
    private let systemImage: String
    private let title: Text
    private let detail: Text?
    private let isOn: Binding<Bool>
    @Environment(\.eControlTheme) private var theme

    public init(systemImage: String, title: Text, detail: Text? = nil, isOn: Binding<Bool>) {
        self.systemImage = systemImage
        self.title = title
        self.detail = detail
        self.isOn = isOn
    }

    public var body: some View {
        BusinessSettingsRowLayout(
            systemImage: systemImage, title: title, detail: detail, verticalPadding: theme.spacing.formRow,
            trailing: ESwitch(title, isOn: isOn).labelsHidden().controlSize(.small).fixedSize()
        )
    }
}

/// 菜单行。`menu` 内放原生菜单控件（如 `EPicker`）；行本身不可点击。
public struct BusinessMenuRow<Menu: View>: View {
    private let systemImage: String
    private let title: Text
    private let menu: Menu
    @Environment(\.eControlTheme) private var theme

    public init(systemImage: String, title: Text, @ViewBuilder menu: () -> Menu) {
        self.systemImage = systemImage
        self.title = title
        self.menu = menu()
    }

    public var body: some View {
        BusinessSettingsRowLayout(
            systemImage: systemImage, title: title, detail: nil, verticalPadding: theme.spacing.inline * 2,
            trailing: menu
        )
    }
}

/// 可点行，右侧显示 chevron，用于打开 sheet 或二级页面。
public struct BusinessNavRow: View {
    private let systemImage: String
    private let title: Text
    private let detail: Text?
    private let action: () -> Void
    @Environment(\.eControlTheme) private var theme

    public init(systemImage: String, title: Text, detail: Text? = nil, action: @escaping () -> Void) {
        self.systemImage = systemImage
        self.title = title
        self.detail = detail
        self.action = action
    }

    public var body: some View {
        EButton(emphasis: .plain, action: action) {
            BusinessSettingsRowLayout(
                systemImage: systemImage, title: title, detail: detail, verticalPadding: theme.spacing.formRow,
                trailing: Image(systemName: "chevron.right")
                    .font(theme.typography.secondary)
                    .foregroundStyle(theme.colors.tertiaryText)
                    .accessibilityHidden(true)
            )
            .contentShape(Rectangle())
        }
    }
}
#endif
