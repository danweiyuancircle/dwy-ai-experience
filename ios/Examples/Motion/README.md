# DesignCore Motion 示例

同一份 SwiftUI 页面展示排序、反馈转场、指针悬停，并显示系统真实的减少动态效果状态。示例状态只在内存中，不改变系统偏好。

macOS：从仓库根运行 `swift run MotionGallery`。

iOS：在 `ios/Examples/Motion` 运行 `xcodegen generate`，打开生成的 `MotionGallery.xcodeproj`，在已有 iOS 18+ 模拟器运行。工程直接使用同一仓库的 DesignCore 源码，不需要发布或安装新依赖。Xcode 工程为本地生成物。

开启系统“辅助功能 → 减少动态效果”后再次点击排序和反馈按钮：布局和缩放应立即更新，不应继续弹动。快速重复点击不会排队执行业务动作。原生按钮自带反馈，不叠加 scalePress。
