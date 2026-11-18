#if os(macOS)
import AppKit
import SwiftUI

public extension View {
    /// 用在原生分栏的侧栏内容上，阻止该栏被折叠。调用方仍负责列宽和工具栏入口。
    func ePreventsSidebarCollapse() -> some View {
        background(ESidebarCollapseGuard())
    }
}

private struct ESidebarCollapseGuard: NSViewRepresentable {
    func makeNSView(context: Context) -> SidebarCollapseAttachment { SidebarCollapseAttachment() }
    func updateNSView(_ view: SidebarCollapseAttachment, context: Context) {}
}

final class SidebarCollapseAttachment: NSView {
    override func viewDidMoveToWindow() {
        super.viewDidMoveToWindow()
        guard window != nil else { return }
        // 原生视图的响应者链可能跳过分栏控制器，通过其分栏视图定位所属控制器。
        var ancestor = superview
        while let current = ancestor {
            if let splitView = current as? NSSplitView,
               let controller = splitView.delegate as? NSSplitViewController,
               let item = controller.splitViewItems.first(where: { isDescendant(of: $0.viewController.view) }) {
                item.canCollapse = false
                return
            }
            ancestor = current.superview
        }
    }
}
#endif
