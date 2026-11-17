#if os(macOS)
import AppKit
import SwiftUI

/// 通用工具面板宿主；任务、授权和模态返回值由业务控制，不在关闭时推断取消。
@MainActor
open class EToolPanel: NSPanel {
    /// 任务窗口可关闭性须由宿主显式选择；不自动中止业务任务。
    public init(title: String, size: NSSize, closable: Bool = true) {
        super.init(contentRect: NSRect(origin: .zero, size: size),
                   styleMask: closable ? [.titled, .closable] : [.titled], backing: .buffered, defer: false)
        self.title = title
        isReleasedWhenClosed = false
        hidesOnDeactivate = false
    }

    /// 每个独立宿主显式设置共享控件主题；语言、主题管理器等业务环境由内容注入。
    public func setContent<Content: View>(@ViewBuilder content: () -> Content) {
        contentView = NSHostingView(rootView: content().eControlTheme(.standard))
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
