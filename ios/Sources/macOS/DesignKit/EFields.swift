#if os(macOS)
import SwiftUI

/// 单行原生输入，不转换、截断或持久化业务输入；焦点和 onSubmit 仍由宿主控制。
public struct ETextField: View {
    private let title: Text
    @Binding private var text: String

    public init(_ title: LocalizedStringResource, text: Binding<String>) {
        self.init(Text(title), text: text)
    }

    /// Text 保留调用方的 bundle、插值及 verbatim 语义。
    public init(_ title: Text, text: Binding<String>) {
        self.title = title
        self._text = text
    }

    public var body: some View {
        TextField(text: $text) { title }.textFieldStyle(.plain).modifier(EFieldChrome())
    }
}

/// 原生安全输入，密码仅通过绑定回写，库不记录或转成普通文本展示。
public struct ESecureField: View {
    private let title: Text
    @Binding private var text: String

    public init(_ title: LocalizedStringResource, text: Binding<String>) {
        self.init(Text(title), text: text)
    }

    public init(_ title: Text, text: Binding<String>) {
        self.title = title
        self._text = text
    }

    public var body: some View {
        SecureField(text: $text) { title }.textFieldStyle(.plain).modifier(EFieldChrome())
    }
}

/// 标签、输入槽与说明组合；校验与提交属于宿主，错误优先于普通说明。
public struct EField<Content: View>: View {
    @Environment(\.eControlTheme) private var theme
    private let title: Text
    private let hint: Text?
    private let error: Text?
    private let content: Content

    public init(_ title: LocalizedStringResource, hint: LocalizedStringResource? = nil,
                error: LocalizedStringResource? = nil, @ViewBuilder content: () -> Content) {
        self.init(Text(title), hint: hint.map { Text($0) }, error: error.map { Text($0) }, content: content)
    }

    /// 原文消息通过 Text(verbatim:) 传入，避免把用户内容误当本地化 key。
    public init(_ title: Text, hint: Text? = nil, error: Text? = nil, @ViewBuilder content: () -> Content) {
        self.title = title
        self.hint = hint
        self.error = error
        self.content = content()
    }

    public var body: some View {
        VStack(alignment: .leading, spacing: theme.spacing.fieldLabel) {
            title.font(theme.typography.secondary).foregroundStyle(theme.colors.secondaryText)
            content.accessibilityLabel(title)
            if let error {
                error.font(theme.typography.secondary).foregroundStyle(theme.colors.danger)
                    .fixedSize(horizontal: false, vertical: true)
            } else if let hint {
                hint.font(theme.typography.secondary).foregroundStyle(theme.colors.secondaryText)
                    .fixedSize(horizontal: false, vertical: true)
            }
        }
        .accessibilityElement(children: .contain)
    }
}

/// 搜索输入仅即时回写绑定，清空不等于提交或删除历史。
public struct ESearchField: View {
    @Environment(\.eControlTheme) private var theme
    private let title: Text
    private let clearTitle: Text
    @Binding private var text: String

    public init(_ title: LocalizedStringResource, text: Binding<String>, clearTitle: LocalizedStringResource) {
        self.init(Text(title), text: text, clearTitle: Text(clearTitle))
    }

    public init(_ title: Text, text: Binding<String>, clearTitle: Text) {
        self.title = title
        self._text = text
        self.clearTitle = clearTitle
    }

    public var body: some View {
        HStack(spacing: theme.spacing.fieldLabel) {
            Image(systemName: "magnifyingglass").foregroundStyle(.secondary).accessibilityHidden(true)
            TextField(text: $text) { title }.textFieldStyle(.plain)
            if !text.isEmpty {
                Button { text = "" } label: {
                    Image(systemName: "xmark.circle.fill")
                }
                .accessibilityLabel(clearTitle)
                .help(clearTitle)
                .buttonStyle(.borderless)
            }
        }
        .modifier(EFieldChrome(isSearch: true))
    }
}

/// 可滚动表单正文和保持可达的右对齐动作；不注册 Enter/Esc 或执行业务校验。
public struct EForm<Content: View, Actions: View>: View {
    @Environment(\.eControlTheme) private var theme
    private let content: Content
    private let actions: Actions

    public init(@ViewBuilder content: () -> Content, @ViewBuilder actions: () -> Actions) {
        self.content = content()
        self.actions = actions()
    }

    public var body: some View {
        VStack(spacing: theme.spacing.group) {
            ScrollView {
                VStack(alignment: .leading, spacing: theme.spacing.formRow) { content }
                    .frame(maxWidth: .infinity, alignment: .leading)
            }
            Divider()
            HStack { Spacer(minLength: 0); actions }
        }
    }
}
#endif
