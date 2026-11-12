#if os(macOS)
import SwiftUI

/// 原生动作菜单。选项传 Label 时保留其图标，纯 Text 不补图标；原生角色、分组与子菜单语义不变。
public struct EMenu<Label: View, Content: View>: View {
    private let label: Label
    private let content: Content

    /// 自定义触发标签支持图标与图片；仅图标时调用方须提供 accessibilityLabel。
    public init(@ViewBuilder content: () -> Content, @ViewBuilder label: () -> Label) {
        self.content = content()
        self.label = label()
    }

    /// title 由应用本地化；菜单项及其状态仍交给系统渲染。
    public init(_ title: LocalizedStringResource, @ViewBuilder content: () -> Content) where Label == Text {
        self.init(content: content) { Text(title) }
    }

    public var body: some View {
        // macOS 27 默认减少符号图标；在原生 Menu 上明确保留调用方提供的图文标签。
        Menu(content: { content }, label: { label })
            .labelStyle(.titleAndIcon)
            .modifier(EButtonChrome(emphasis: .secondary))
    }
}

/// 单选的原生呈现方式，共用强类型选择绑定。
public enum EPickerPresentation: Sendable {
    case menu
    case segmented
}

/// 原生单选控件。每个选项的 tag 类型须与 Selection 一致；选择与保存由业务负责。
public struct EPicker<Selection: Hashable, Content: View>: View {
    private let title: Text
    @Binding private var selection: Selection
    private let presentation: EPickerPresentation
    private let content: Content

    /// 菜单选项可用 Label 提供图标或 Text 只显示文字；保留 ForEach、禁用与强类型 tag 语义。
    public init(
        _ title: LocalizedStringResource,
        selection: Binding<Selection>,
        presentation: EPickerPresentation = .menu,
        @ViewBuilder content: () -> Content
    ) {
        self.init(Text(title), selection: selection, presentation: presentation, content: content)
    }

    /// 原文或调用方 Text 标签；选项必须使用与 Selection 一致的稳定 tag。
    public init(_ title: Text, selection: Binding<Selection>, presentation: EPickerPresentation = .menu,
                @ViewBuilder content: () -> Content) {
        self.title = title
        self._selection = selection
        self.presentation = presentation
        self.content = content()
    }

    public var body: some View {
        let picker = Picker(selection: $selection) { content } label: { title }
        switch presentation {
        case .menu: picker.pickerStyle(.menu).labelStyle(.titleAndIcon)
        case .segmented: picker.pickerStyle(.segmented)
        }
    }
}

/// Mac 原生开关，显式采用 switch 呈现，防止无标签时变为难辨认的 checkbox。
public struct ESwitch: View {
    private let title: Text
    @Binding private var isOn: Bool

    /// title 保留可访问名称，隐藏可见标题时可在调用处使用 labelsHidden。
    public init(_ title: LocalizedStringResource, isOn: Binding<Bool>) {
        self.init(Text(title), isOn: isOn)
    }

    public init(_ title: Text, isOn: Binding<Bool>) {
        self.title = title
        self._isOn = isOn
    }

    public var body: some View {
        Toggle(isOn: $isOn) { title }.toggleStyle(.switch)
    }
}
/// 桌面复选框；菜单内仍使用原生 Toggle 的菜单勾选语义。
public struct ECheckbox: View {
    private let title: Text
    @Binding private var isOn: Bool

    /// 标题兼作可访问名称，隐藏视觉标签时仍须保留有意义的名称。
    public init(_ title: LocalizedStringResource, isOn: Binding<Bool>) {
        self.init(Text(title), isOn: isOn)
    }

    public init(_ title: Text, isOn: Binding<Bool>) {
        self.title = title
        self._isOn = isOn
    }

    public var body: some View {
        Toggle(isOn: $isOn) { title }.toggleStyle(.checkbox)
    }
}
#endif
