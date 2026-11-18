#if os(macOS)
import SwiftUI

public extension View {
    /// 在当前内容区居中呈现弹框，保持底层布局和亮度。调用方负责外观、路由与关闭后的状态。
    func eWindowOverlay<Panel: View>(
        isPresented: Bool,
        preferredSize: CGSize,
        onDismiss: @escaping () -> Void,
        @ViewBuilder panel: @escaping () -> Panel
    ) -> some View {
        accessibilityElement(children: .contain)
            .accessibilityHidden(isPresented)
            .overlay {
                if isPresented {
                    GeometryReader { geometry in
                        let size = EWindowOverlayLayout.size(preferred: preferredSize, available: geometry.size)
                        panel()
                            .frame(width: size.width, height: size.height)
                            .frame(maxWidth: .infinity, maxHeight: .infinity)
                            .background {
                                Color.clear.contentShape(Rectangle()).onTapGesture {}
                            }
                    }
                    .background {
                        // 让 Esc 在底页触发按钮仍持有焦点时也能关闭弹框。
                        Button(action: onDismiss) { EmptyView() }
                            .keyboardShortcut(.cancelAction)
                            .accessibilityHidden(true)
                    }
                }
            }
    }
}

enum EWindowOverlayLayout {
    static func size(preferred: CGSize, available: CGSize) -> CGSize {
        CGSize(width: max(0, min(preferred.width, available.width - 40)),
               height: max(0, min(preferred.height, available.height - 40)))
    }
}
#endif
