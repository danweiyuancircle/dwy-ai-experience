#if os(macOS)
import AppKit
import SwiftUI
import UniformTypeIdentifiers

/// 确认按钮的系统语义；顺序仍对应 NSAlert 的原生返回码。
public enum EAlertActionRole: Sendable { case normal, cancel, destructive }

/// 文案由宿主解析，组件不持有业务状态或执行文件操作。
public struct EAlertAction: Sendable {
    public let title: String
    public let role: EAlertActionRole
    /// title 为已本地化文案；role 只决定系统交互语义，不执行回调。
    public init(_ title: String, role: EAlertActionRole = .normal) {
        self.title = title
        self.role = role
    }
}

/// AppKit 与 SwiftUI 宿主共用的系统对话框。取消与按钮返回码不转换为业务成功。
@MainActor
public final class EAlert {
    let nativeAlert: NSAlert

    /// 至少显式提供一个操作，危险操作不绑定 Return，取消保留 Escape。
    public init(title: String, message: String = "", style: NSAlert.Style = .informational,
                actions: [EAlertAction]) {
        precondition(!actions.isEmpty, "An alert requires an explicit action")
        nativeAlert = NSAlert()
        nativeAlert.messageText = title
        nativeAlert.informativeText = message
        nativeAlert.alertStyle = style
        for action in actions {
            let button = nativeAlert.addButton(withTitle: action.title)
            if action.role == .destructive {
                button.hasDestructiveAction = true
                button.keyEquivalent = ""
            } else if action.role == .cancel {
                button.keyEquivalent = "\u{1b}"
            }
        }
    }

    /// 输入控件和校验由宿主提供；对话框关闭后宿主负责清空敏感输入。
    public var accessoryView: NSView? {
        get { nativeAlert.accessoryView }
        set { nativeAlert.accessoryView = newValue }
    }

    /// 仅用于已有操作的即时校验，不在组件内猜测业务输入有效性。
    public func setActionEnabled(_ enabled: Bool, at index: Int) { nativeAlert.buttons[index].isEnabled = enabled }

    /// 激活无主窗口的菜单栏应用；返回系统按钮码，调用方必须处理取消和失败。
    @discardableResult public func runModal() -> NSApplication.ModalResponse {
        NSApp.activate(ignoringOtherApps: true)
        return nativeAlert.runModal()
    }
}

/// 文件选择器仅收集 URL；隐式 security scope 的所有权和书签生命周期仍由调用方管理。
@MainActor
public enum EFileDialog {
    enum Selection { case files, directories }

    /// 单选目录，取消返回 nil；选择后调用方接管系统隐式授权。
    public static func chooseDirectory(title: String? = nil, directory: URL? = nil,
                                       message: String? = nil, prompt: String? = nil) -> URL? {
        choose(selection: .directories, title: title, directory: directory, message: message, prompt: prompt)
    }

    /// 单选文件并保留类型限制；空类型数组使用系统默认的任意文件选择。
    public static func chooseFile(title: String? = nil, directory: URL? = nil, message: String? = nil,
                                  prompt: String? = nil, allowedContentTypes: [UTType] = []) -> URL? {
        choose(selection: .files, title: title, directory: directory, message: message, prompt: prompt,
               allowedContentTypes: allowedContentTypes)
    }

    private static func choose(selection: Selection, title: String?, directory: URL?, message: String?,
                               prompt: String?, allowedContentTypes: [UTType] = []) -> URL? {
        let panel = makePanel(selection: selection, title: title, directory: directory, message: message,
                              prompt: prompt, allowedContentTypes: allowedContentTypes)
        NSApp.activate(ignoringOtherApps: true)
        return result(for: panel.runModal(), panel: panel)
    }

    static func makePanel(selection: Selection, title: String? = nil, directory: URL? = nil,
                          message: String? = nil, prompt: String? = nil,
                          allowedContentTypes: [UTType] = []) -> NSOpenPanel {
        let panel = NSOpenPanel()
        panel.canChooseFiles = selection == .files
        panel.canChooseDirectories = selection == .directories
        panel.allowsMultipleSelection = false
        panel.directoryURL = directory
        if let title { panel.title = title }
        if let message { panel.message = message }
        if let prompt { panel.prompt = prompt }
        if !allowedContentTypes.isEmpty { panel.allowedContentTypes = allowedContentTypes }
        return panel
    }

    static func result(for response: NSApplication.ModalResponse, panel: NSOpenPanel) -> URL? {
        response == .OK ? panel.url : nil
    }
}

/// 消息非 nil 时显示原生错误弹框；确认和关闭均清空绑定，业务重试由宿主负责。
public struct EErrorAlert: ViewModifier {
    private let title: String
    @Binding private var message: String?
    private let dismissTitle: String

    /// 标题和按钮文案由宿主本地化，错误消息按原文显示。
    public init(title: String, message: Binding<String?>, dismissTitle: String) {
        self.title = title
        _message = message
        self.dismissTitle = dismissTitle
    }

    public func body(content: Content) -> some View {
        content.alert(title, isPresented: Binding(
            get: { message != nil },
            set: { if !$0 { message = nil } }
        )) {
            Button(dismissTitle) { message = nil }
        } message: {
            if let message { Text(verbatim: message) }
        }
    }
}

#endif
