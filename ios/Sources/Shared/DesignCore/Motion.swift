import SwiftUI

/// 全局动效参数，避免各页弹簧不一致。
public enum Motion {
    /// 通用弹簧：轻微回弹。
    public static let spring = Animation.spring(response: 0.42, dampingFraction: 0.92)
    /// 按钮按压：短促、略弹。
    public static let press = Animation.spring(response: 0.22, dampingFraction: 0.78)
    /// 进度条 / 选中态即时反馈。
    public static let snappy = Animation.easeInOut(duration: 0.18)
    /// 环进度、主控显隐：几乎无弹。
    public static let soft = Animation.easeInOut(duration: 0.24)
    /// 页面进出：纯淡入淡出。
    public static let page = Animation.easeInOut(duration: 0.2)
    /// 遮罩层：略慢于 page。
    public static let overlay = Animation.easeInOut(duration: 0.24)
}

/// 轻量按压缩放。
public struct ScalePressButtonStyle: ButtonStyle {
    public init() {}

    public func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .scaleEffect(configuration.isPressed ? 0.94 : 1)
            .opacity(configuration.isPressed ? 0.86 : 1)
            .animation(Motion.press, value: configuration.isPressed)
    }
}

public extension View {
    /// 应用轻按压风格。
    func scalePress() -> some View {
        buttonStyle(ScalePressButtonStyle())
    }
}
