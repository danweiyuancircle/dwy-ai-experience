#if os(iOS)
import SwiftUI

/// 原生编辑器外壳。输入配置、FocusState 和 onSubmit 沿用 SwiftUI，不改写组合输入。
public struct EFieldShell<Content: View>: View {
    @Environment(\.eControlTheme) private var theme
    @Environment(\.displayScale) private var displayScale
    private let isInvalid: Bool
    private let content: Content

    public init(isInvalid: Bool = false, @ViewBuilder content: () -> Content) {
        self.isInvalid = isInvalid
        self.content = content()
    }

    public var body: some View {
        content
            .font(theme.typography.body)
            .textFieldStyle(.plain)
            .padding(.horizontal, theme.spacing.formRow)
            .frame(minHeight: theme.size.field)
            .background(theme.colors.surface, in: RoundedRectangle(cornerRadius: theme.radius.field))
            .overlay {
                RoundedRectangle(cornerRadius: theme.radius.field)
                    .strokeBorder(
                        isInvalid ? theme.colors.danger : theme.colors.separator,
                        lineWidth: theme.hairline(displayScale: displayScale)
                    )
            }
    }
}

/// 单行原生文本框；不 trim、截断、保存历史或替业务校验。
public struct ETextField: View {
    @Environment(\.eControlTheme) private var theme
    @Binding private var text: String
    private let title: Text
    private let prompt: Text?
    private let isInvalid: Bool

    public init(_ title: Text, text: Binding<String>, prompt: Text? = nil, isInvalid: Bool = false) {
        self.title = title
        _text = text
        self.prompt = prompt
        self.isInvalid = isInvalid
    }

    public var body: some View {
        EFieldShell(isInvalid: isInvalid) {
            TextField(text: $text, prompt: prompt) { title }
                .frame(minHeight: theme.size.field)
        }
    }
}

/// 密码始终使用 SecureField，保留原生安全输入与 AutoFill 配置。
public struct ESecureField: View {
    @Environment(\.eControlTheme) private var theme
    @Binding private var text: String
    private let title: Text
    private let prompt: Text?
    private let isInvalid: Bool

    public init(_ title: Text, text: Binding<String>, prompt: Text? = nil, isInvalid: Bool = false) {
        self.title = title
        _text = text
        self.prompt = prompt
        self.isInvalid = isInvalid
    }

    public var body: some View {
        EFieldShell(isInvalid: isInvalid) {
            SecureField(text: $text, prompt: prompt) { title }
                .frame(minHeight: theme.size.field)
        }
    }
}

/// 搜索只读写当前字符串；清空名称由产品本地化提供，不隐式执行请求或删除历史。
public struct ESearchField: View {
    @Environment(\.eControlTheme) private var theme
    @Binding private var text: String
    private let title: Text
    private let clearLabel: Text

    public init(_ title: Text, text: Binding<String>, clearLabel: Text) {
        self.title = title
        _text = text
        self.clearLabel = clearLabel
    }

    public var body: some View {
        EFieldShell {
            HStack(spacing: theme.spacing.controlGroup) {
                Image(systemName: "magnifyingglass").foregroundStyle(.secondary).accessibilityHidden(true)
                TextField(text: $text) { title }
                    .frame(minHeight: theme.size.search)
                if !text.isEmpty {
                    Button { text = "" } label: {
                        Image(systemName: "xmark.circle.fill")
                            .frame(minWidth: theme.size.iconHit, minHeight: theme.size.iconHit)
                    }
                    .buttonStyle(.borderless)
                    .accessibilityLabel(clearLabel)
                }
            }
        }
    }
}

/// 表单字段的标签和说明组合；错误优先于 hint，不自动清值或移动焦点。
/// 原生编辑器仍需带自己的可访问标题，避免 VoiceOver 只读到装饰标签。
public struct EField<Label: View, Content: View>: View {
    @Environment(\.eControlTheme) private var theme
    private let label: Label
    private let hint: Text?
    private let error: Text?
    private let content: Content

    public init(
        hint: Text? = nil,
        error: Text? = nil,
        @ViewBuilder label: () -> Label,
        @ViewBuilder content: () -> Content
    ) {
        self.hint = hint
        self.error = error
        self.label = label()
        self.content = content()
    }

    public var body: some View {
        VStack(alignment: .leading, spacing: theme.spacing.fieldLabel) {
            label.font(theme.typography.sectionTitle)
            content
            if let error {
                SwiftUI.Label { error } icon: { Image(systemName: "exclamationmark.circle") }
                    .font(theme.typography.caption)
                    .foregroundStyle(theme.colors.danger)
            } else if let hint {
                hint.font(theme.typography.caption).foregroundStyle(.secondary)
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
    }
}

/// 移动端动作区纵向铺满；按钮角色及提交/取消行为由调用方显式提供。
public struct EActionGroup<Content: View>: View {
    @Environment(\.eControlTheme) private var theme
    private let content: Content

    public init(@ViewBuilder content: () -> Content) { self.content = content() }

    public var body: some View {
        VStack(spacing: theme.spacing.controlGroup) { content }
            .environment(\.eActionGroupExpandsButtons, true)
    }
}

private struct EActionGroupExpandsButtonsKey: EnvironmentKey {
    static let defaultValue = false
}

extension EnvironmentValues {
    var eActionGroupExpandsButtons: Bool {
        get { self[EActionGroupExpandsButtonsKey.self] }
        set { self[EActionGroupExpandsButtonsKey.self] = newValue }
    }
}

/// 滚动表单不固定高度；宿主通过自己的 FocusState/键盘工具栏提供主动收键盘路径。
public struct EForm<Content: View>: View {
    @Environment(\.eControlTheme) private var theme
    @Environment(\.horizontalSizeClass) private var sizeClass
    private let content: Content

    public init(@ViewBuilder content: () -> Content) { self.content = content() }

    public var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: theme.spacing.section) { content }
                .padding(theme.spacing.pageInset(horizontalSizeClass: sizeClass))
        }
        .scrollDismissesKeyboard(.interactively)
        .background(theme.colors.background)
    }
}

#endif
