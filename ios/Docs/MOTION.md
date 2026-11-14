# 原生 SwiftUI 动效

动效入口属于 `DesignCore`，支持 iOS 18+、macOS 26+，不需要第三方动画库。消费方链接 `DesignCore` 后 `import DesignCore` 即可使用。

```swift
import SwiftUI
import DesignCore

struct FeedbackExample: View {
    @State private var completed = false

    var body: some View {
        VStack {
            Button("切换反馈") { completed.toggle() }
            if completed {
                Label("已完成", systemImage: "checkmark.circle")
                    .eTransition(.softMove)
            }
        }
        .eMotion(.feedback, value: completed)
    }
}
```

| 入口 | 使用范围 |
| --- | --- |
| `.eMotion(.hover, value:)` | 自绘区域的指针高亮 |
| `.eMotion(.selection, value:)` | 局部选中态 |
| `.eMotion(.reorder, value:)` | 稳定 ID 的列表排序、增删 |
| `.eMotion(.page, value:)` | 局部内容切换 |
| `.eMotion(.feedback, value:)` | 提示或结果出现 |
| `.eTransition(.fade)` / `.eTransition(.softMove)` | 只声明淡入或淡入加 6 pt 位移，需父容器动画驱动 |
| `.scalePress()` | 自绘按钮按压；系统按钮无需重复添加 |

入口读取真实 `accessibilityReduceMotion`。开启减少动态效果后，`eMotion` 返回无动画；`softMove` 退为 opacity 转场，但不自行启动动画，因此通常立即呈现。按压保留透明度反馈、取消缩放。旧 `Motion.*` 常量仍兼容，直接使用它们的代码需要自行处理系统设置。

只将修饰符加在变化的小区域，避免整个根视图、窗口尺寸、侧栏布局或文本输入跟着动画。`value` 只是动画触发值，不延迟、重试或执行操作；列表必须由业务提供稳定 ID。原生 sheet、菜单、开关、导航和玻璃反馈沿用系统行为。

## 示例与验证

完整双平台示例位于 `ios/Examples/Motion`。根目录执行 `swift run MotionGallery` 可运行 Mac 示例；iOS 示例生成方式见该目录 README。测试执行 `swift test --filter MotionTests`，覆盖预设、减少动态效果策略及原有按压 API 兼容。

ADBox 首批接入 Mac 设备卡悬停、Mac 提示条和 iOS 发现结果角标。RightFlow 的共享 macOS UI 接入独立使用 `DesignKitMac`，不需要将业务菜单实现移到基础库。

本轮 API 尚未发布。消费方本地 workspace 通过名为 `dwy-ai-experience` 的符号链接覆盖同名远程包；正式版本声明和锁文件保持原状。正式分发前需发布包含这些 API 的共享版本，再更新消费方依赖，不能重打旧标签。
