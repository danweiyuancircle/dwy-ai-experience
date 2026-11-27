#if os(iOS)
import SwiftUI

/// 单按钮原生提示框；挂载到当前 scene 的视图，文案由宿主提供，关闭后回写呈现绑定。
public struct EAlert: ViewModifier {
    private let title: Text
    private let message: Text
    @Binding private var isPresented: Bool
    private let dismissTitle: Text

    public init(title: Text, message: Text, isPresented: Binding<Bool>, dismissTitle: Text) {
        self.title = title
        self.message = message
        _isPresented = isPresented
        self.dismissTitle = dismissTitle
    }

    public func body(content: Content) -> some View {
        content.alert(title, isPresented: $isPresented) {
            Button(role: .cancel, action: {}) { dismissTitle }
        } message: {
            message
        }
    }
}

/// 原生二次确认框；取消不执行业务动作，确认回调只表达用户意图，不代表异步任务成功。
/// 宿主在打开时固定业务目标，避免选择变化后确认到另一对象。
public struct EConfirm: ViewModifier {
    private let title: Text
    private let message: Text
    @Binding private var isPresented: Bool
    private let confirmTitle: Text
    private let cancelTitle: Text
    private let isDestructive: Bool
    private let onConfirm: () -> Void

    public init(
        title: Text, message: Text, isPresented: Binding<Bool>, confirmTitle: Text, cancelTitle: Text,
        isDestructive: Bool = false, onConfirm: @escaping () -> Void
    ) {
        self.title = title
        self.message = message
        _isPresented = isPresented
        self.confirmTitle = confirmTitle
        self.cancelTitle = cancelTitle
        self.isDestructive = isDestructive
        self.onConfirm = onConfirm
    }

    public func body(content: Content) -> some View {
        content.alert(title, isPresented: $isPresented) {
            Button(role: .cancel, action: {}) { cancelTitle }
            Button(role: isDestructive ? .destructive : nil, action: onConfirm) { confirmTitle }
        } message: {
            message
        }
    }
}

/// 消息非 nil 时触发原生错误提示；消息按原文显示，关闭清空绑定，不计时消失或隐式重试。
public struct EErrorAlert: ViewModifier {
    private let title: Text
    @Binding private var message: String?
    private let dismissTitle: Text

    public init(title: Text, message: Binding<String?>, dismissTitle: Text) {
        self.title = title
        _message = message
        self.dismissTitle = dismissTitle
    }

    public func body(content: Content) -> some View {
        content.alert(title, isPresented: Binding(
            get: { message != nil },
            set: { if !$0 { message = nil } }
        )) {
            Button(role: .cancel) { message = nil } label: { dismissTitle }
        } message: {
            if let message { Text(verbatim: message) }
        }
    }
}
#endif
