#if os(macOS)
import AppKit
import SwiftUI

/// 用同一窗口标识连接 SwiftUI、Window 菜单和 Dock 重开。每个应用自行决定新建哪个场景。
@MainActor
public struct EMainWindow {
    public let identifier: NSUserInterfaceItemIdentifier

    /// 标识应与设置窗和工具窗区分。SwiftUI 用 `marker` 标记，AppKit 可直接设置窗口的 identifier。
    public init(id: String) {
        identifier = NSUserInterfaceItemIdentifier(id)
    }

    /// 从显式菜单入口调用。有目标窗就调前，必要时恢复最小化，否则调用宿主的开窗动作。
    public func show(in application: NSApplication = .shared, open: () -> Void) {
        if let window = target(in: application.windows) {
            if window.isMiniaturized { window.deminiaturize(nil) }
            window.makeKeyAndOrderFront(nil)
        } else {
            open()
        }
        application.activate()
    }

    /// 在 `applicationShouldHandleReopen` 中返回此结果。已处理的重开交还 false，避免系统重复建窗。
    public func handleDockReopen(in application: NSApplication, hasVisibleWindows: Bool, open: () -> Void) -> Bool {
        guard !hasVisibleWindows else { return true }
        show(in: application, open: open)
        return false
    }

    /// 挂到目标场景内容的 background，等 SwiftUI 把视图装进 NSWindow 后再标记。
    public var marker: some View {
        EMainWindowMarker(identifier: identifier)
            .frame(width: 0, height: 0)
            .allowsHitTesting(false)
            .accessibilityHidden(true)
    }

    func target(in windows: [NSWindow]) -> NSWindow? {
        windows.first { $0.identifier == identifier && !$0.isMiniaturized }
            ?? windows.first { $0.identifier == identifier }
    }
}

private struct EMainWindowMarker: NSViewRepresentable {
    let identifier: NSUserInterfaceItemIdentifier

    func makeNSView(context: Context) -> MarkerView { MarkerView() }
    func updateNSView(_ view: MarkerView, context: Context) {
        view.identifier = identifier
        view.markWindow()
    }

    final class MarkerView: NSView {
        override func viewDidMoveToWindow() {
            super.viewDidMoveToWindow()
            markWindow()
        }

        func markWindow() {
            if let identifier { window?.identifier = identifier }
        }
    }
}

/// 可调整尺寸的独立工具窗；代理与内容替换策略由宿主业务持有。
@MainActor
public final class EToolWindow: NSWindow {
    /// size 是初始产品尺寸，后续最小尺寸和窗口代理由宿主设置。
    public init(title: String, size: NSSize) {
        super.init(contentRect: NSRect(origin: .zero, size: size),
                   styleMask: [.titled, .closable, .miniaturizable, .resizable], backing: .buffered, defer: false)
        self.title = title
        isReleasedWhenClosed = false
    }

    public func setContent<Content: View>(@ViewBuilder content: () -> Content) {
        contentView = NSHostingView(rootView: content().eControlTheme(.standard))
    }
}

/// Settings 场景的标题栏策略在实际挂载后应用，避免各项目依赖 SwiftUI 的窗口创建时序。
public struct ESettingsWindowChrome: NSViewRepresentable {
    public init() {}
    public func makeNSView(context: Context) -> TitleView { TitleView() }
    public func updateNSView(_ view: TitleView, context: Context) {}

    /// 可用于 AppKit 宿主；只在接入窗口时调整样式，不随每次 SwiftUI 更新反复布局。
    public final class TitleView: NSView {
        public override func viewDidMoveToWindow() {
            super.viewDidMoveToWindow()
            window?.styleMask.formUnion([.miniaturizable, .resizable])
            window?.titleVisibility = .visible
            window?.titlebarAppearsTransparent = true
            window?.toolbarStyle = .unifiedCompact
        }
    }
}
#endif
