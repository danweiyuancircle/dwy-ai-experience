import SwiftUI

/// 跨平台交互动效语义；仅改变呈现，不调度业务操作或写入状态。
public enum EMotionPreset: CaseIterable, Sendable {
    case hover, selection, reorder, page, feedback

    /// 减少动态效果时关闭布局、缩放及弹簧动画；原生控件仍提供其系统反馈。
    public func animation(reduceMotion: Bool) -> Animation? {
        guard !reduceMotion else { return nil }
        switch self {
        case .hover: return .easeOut(duration: 0.12)
        case .selection: return Motion.snappy
        case .reorder: return Motion.spring
        case .page: return Motion.page
        case .feedback: return Motion.soft
        }
    }
}

/// 短内容的插入与移除效果；需要宿主在变化区域用 eMotion 或显式动画驱动。
public enum EMotionTransition: Sendable {
    case fade, softMove

    func resolved(reduceMotion: Bool) -> Self {
        reduceMotion ? .fade : self
    }

    var transition: AnyTransition {
        switch self {
        case .fade: return .opacity
        case .softMove: return .opacity.combined(with: .offset(y: 6))
        }
    }
}

private struct EMotionModifier<Value: Equatable>: ViewModifier {
    let preset: EMotionPreset
    let value: Value
    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    func body(content: Content) -> some View {
        content.animation(preset.animation(reduceMotion: reduceMotion), value: value)
    }
}

private struct EMotionTransitionModifier: ViewModifier {
    let style: EMotionTransition
    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    func body(content: Content) -> some View {
        content.transition(style.resolved(reduceMotion: reduceMotion).transition)
    }
}

public extension View {
    /// 仅响应指定值的变化。列表传稳定 ID 序列；放在最小变化区域，避免动画化窗口尺寸或输入焦点。
    func eMotion<Value: Equatable>(_ preset: EMotionPreset, value: Value) -> some View {
        modifier(EMotionModifier(preset: preset, value: value))
    }

    /// 声明内容转场，不自行改变可见状态；减少动态效果时移除位移，并保留视图结构身份。
    func eTransition(_ style: EMotionTransition) -> some View {
        modifier(EMotionTransitionModifier(style: style))
    }
}
