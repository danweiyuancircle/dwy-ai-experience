#if os(macOS)
import AppKit
import SwiftUI

public extension View {
    /// 在稳定的内容区根呈现透明背景的模态弹框，并隔离所属窗口的输入、管理焦点。
    /// 调用方提供面板外观、在 onDismiss 中更新状态，并按同一状态禁用应用级业务菜单与自行安装的事件监听。
    func eWindowOverlay<Panel: View>(
        isPresented: Bool,
        preferredSize: CGSize,
        onDismiss: @escaping () -> Void,
        @ViewBuilder panel: @escaping () -> Panel
    ) -> some View {
        disabled(isPresented)
            .accessibilityElement(children: .contain)
            .accessibilityHidden(isPresented)
            .overlay {
                if isPresented {
                    GeometryReader { geometry in
                        let size = EWindowOverlayLayout.size(preferred: preferredSize, available: geometry.size)
                        EWindowOverlayHost(panel: panel(), panelSize: size, onDismiss: onDismiss)
                    }
                }
            }
    }
}

private struct EWindowOverlayHost<Panel: View>: NSViewRepresentable {
    var panel: Panel
    var panelSize: CGSize
    var onDismiss: () -> Void

    func makeNSView(context: Context) -> EWindowOverlayInputView {
        // AppKit 边界单独承载弹框，避免底页和弹框共用 HostingView 的命令路由。
        let hosting = NSHostingView(rootView: AnyView(panel.environment(\.self, context.environment)))
        hosting.sizingOptions = []
        return EWindowOverlayInputView(panel: hosting, panelSize: panelSize, onDismiss: onDismiss)
    }

    func updateNSView(_ view: EWindowOverlayInputView, context: Context) {
        (view.panel as! NSHostingView<AnyView>).rootView = AnyView(panel.environment(\.self, context.environment))
        view.panelSize = panelSize
        view.onDismiss = onDismiss
        view.needsLayout = true
    }

    static func dismantleNSView(_ view: EWindowOverlayInputView, coordinator: ()) {
        view.stop()
    }
}

@MainActor
final class EWindowOverlayInputView: NSView {
    private struct Entry { weak var view: EWindowOverlayInputView? }
    private static var active: [Entry] = []
    let panel: NSView
    var panelSize: CGSize
    var onDismiss: () -> Void
    private weak var previousFocus: NSResponder?
    private var monitor: Any?
    private var closeObserver: NSObjectProtocol?
    private var pressedButtons = Set<Int>()

    init(panel: NSView, panelSize: CGSize, onDismiss: @escaping () -> Void) {
        self.panel = panel
        self.panelSize = panelSize
        self.onDismiss = onDismiss
        super.init(frame: .zero)
        addSubview(panel)
    }

    @available(*, unavailable)
    required init?(coder: NSCoder) { fatalError("init(coder:) is unavailable") }

    override var acceptsFirstResponder: Bool { true }
    override var isOpaque: Bool { false }

    override func layout() {
        super.layout()
        panel.frame = CGRect(x: (bounds.width - panelSize.width) / 2,
                             y: (bounds.height - panelSize.height) / 2,
                             width: panelSize.width, height: panelSize.height)
        panel.layoutSubtreeIfNeeded()
        if window?.firstResponder === self { focusPanel() }
    }

    override func viewWillMove(toWindow newWindow: NSWindow?) {
        if newWindow !== window { stop() }
        super.viewWillMove(toWindow: newWindow)
    }

    override func viewDidMoveToWindow() {
        super.viewDidMoveToWindow()
        guard let window, monitor == nil else { return }
        // NSTextField 共用窗口 field editor，必须保存其控件，而不是即将更换 delegate 的 editor。
        previousFocus = (window.firstResponder as? NSTextView)?.delegate as? NSView ?? window.firstResponder
        Self.active.removeAll { $0.view == nil }
        Self.active.append(Entry(view: self))
        focusPanel()
        monitor = NSEvent.addLocalMonitorForEvents(matching: [.keyDown, .keyUp, .flagsChanged,
            .leftMouseDown, .leftMouseUp, .rightMouseDown, .rightMouseUp, .otherMouseDown, .otherMouseUp,
            .leftMouseDragged, .rightMouseDragged, .otherMouseDragged, .scrollWheel,
            .mouseMoved, .mouseEntered, .mouseExited, .cursorUpdate,
            .magnify, .smartMagnify, .rotate, .swipe, .beginGesture, .endGesture, .gesture, .pressure]) { [weak self] event in
                let pass = MainActor.assumeIsolated {
                    guard let self else { return true }
                    return self.filter(event) != nil
                }
                return pass ? event : nil
            }
        closeObserver = NotificationCenter.default.addObserver(forName: NSWindow.willCloseNotification,
                                                               object: window, queue: .main) { [weak self] _ in
            MainActor.assumeIsolated { self?.stop() }
        }
    }

    var ownsFirstResponder: Bool {
        guard let responder = window?.firstResponder else { return false }
        if let editor = responder as? NSTextView, editor.isFieldEditor,
           let control = editor.delegate as? NSView {
            return control.isDescendant(of: self)
        }
        return (responder as? NSView)?.isDescendant(of: self) == true
    }

    func stop() {
        guard let monitor else { return }
        let wasTop = Self.active.last(where: { $0.view?.window === window })?.view === self
        NSEvent.removeMonitor(monitor)
        self.monitor = nil
        if let closeObserver { NotificationCenter.default.removeObserver(closeObserver) }
        closeObserver = nil
        pressedButtons.removeAll()
        Self.active.removeAll { $0.view == nil || $0.view === self }
        if wasTop && ownsFirstResponder {
            if let view = previousFocus as? NSView, view.window === window {
                window?.makeFirstResponder(view)
            } else {
                window?.makeFirstResponder(window?.contentView)
            }
        }
        previousFocus = nil
    }

    func filter(_ event: NSEvent) -> NSEvent? {
        guard let window, event.window === window,
              Self.active.last(where: { $0.view?.window === window })?.view === self else { return event }
        switch event.type {
        case .keyDown, .keyUp, .flagsChanged:
            if !ownsFirstResponder { focusPanel() }
            // Command 交回 AppKit 的原生菜单/编辑/SwiftUI shortcut 分发；底页已在 overlay 之外禁用。
            if event.modifierFlags.contains(.command) { return event }
            let responder = window.firstResponder
            if event.type == .keyDown {
                if let editor = responder as? NSTextView, editor.hasMarkedText() {
                    editor.keyDown(with: event)
                } else if event.keyCode == 53 {
                    if !event.isARepeat { onDismiss() }
                } else if event.keyCode == 48 {
                    moveFocus(backward: event.modifierFlags.contains(.shift))
                } else if let editor = responder as? NSTextView, !editor.isFieldEditor,
                          event.keyCode == 36 || event.keyCode == 76 {
                    editor.keyDown(with: event)
                } else if !panel.performKeyEquivalent(with: event) {
                    if responder !== self {
                        responder?.keyDown(with: event)
                    }
                }
            } else if event.type == .keyUp {
                if responder !== self { responder?.keyUp(with: event) }
            } else if responder !== self {
                responder?.flagsChanged(with: event)
            }
            return nil
        default:
            let inside = panel.frame.contains(convert(event.locationInWindow, from: nil))
            switch event.type {
            case .leftMouseDown, .rightMouseDown, .otherMouseDown:
                if inside { pressedButtons.insert(event.buttonNumber) }
                return inside ? event : nil
            case .leftMouseUp, .rightMouseUp, .otherMouseUp:
                return pressedButtons.remove(event.buttonNumber) != nil ? event : nil
            case .leftMouseDragged, .rightMouseDragged, .otherMouseDragged:
                return pressedButtons.contains(event.buttonNumber) ? event : nil
            default:
                return inside ? event : nil
            }
        }
    }

    private func focusPanel() {
        guard let window else { return }
        window.makeFirstResponder(focusableViews(in: panel).first ?? self)
    }

    private func moveFocus(backward: Bool) {
        guard let window else { return }
        let current = (window.firstResponder as? NSTextView)?.delegate as? NSView ?? window.firstResponder as? NSView
        var candidate = backward ? current?.previousValidKeyView : current?.nextValidKeyView
        var visited = Set<ObjectIdentifier>()
        while let view = candidate, visited.insert(ObjectIdentifier(view)).inserted {
            if view !== self, view.isDescendant(of: panel) {
                window.makeFirstResponder(view)
                return
            }
            candidate = backward ? view.previousValidKeyView : view.nextValidKeyView
        }
        let views = focusableViews(in: panel)
        window.makeFirstResponder((backward ? views.last : views.first) ?? self)
    }

    private func focusableViews(in view: NSView) -> [NSView] {
        guard !view.isHiddenOrHasHiddenAncestor else { return [] }
        let children = view.subviews.flatMap { focusableViews(in: $0) }
        return children.isEmpty && view.canBecomeKeyView ? [view] : children
    }

    // 未处理的按键在本承载结束，不能沿 responder chain 到达底页。
    override func keyDown(with event: NSEvent) {}
    override func keyUp(with event: NSEvent) {}
    override func flagsChanged(with event: NSEvent) {}
    override func mouseDown(with event: NSEvent) {}
    override func rightMouseDown(with event: NSEvent) {}
    override func otherMouseDown(with event: NSEvent) {}
    override func scrollWheel(with event: NSEvent) {}
}

enum EWindowOverlayLayout {
    static func size(preferred: CGSize, available: CGSize) -> CGSize {
        CGSize(width: max(0, min(preferred.width, available.width - 40)),
               height: max(0, min(preferred.height, available.height - 40)))
    }
}
#endif
