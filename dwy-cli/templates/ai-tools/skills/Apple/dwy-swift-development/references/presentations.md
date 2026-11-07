# SwiftUI 弹层与锚点

- 需要指向入口的 `popover` 或可能以 popover 呈现的 `confirmationDialog`，把呈现修饰符关联实际触发按钮或行；列表须对应当前目标，工具栏须对应入口。自定义锚点时检查其坐标和所属视图。
- 呈现方式由平台、系统和窗口环境决定；普通系统通知、居中 alert 等不一定有入口锚点，不按弹出位置错误处理。
- 在相关平台验证触发入口、滚动或窗口变化、屏幕边缘、取消和实际目标；以目标系统的交互及视觉为准，编译通过不能证明位置正确。
- 平台差异分别见 `dwy-ios-development` 的弹窗参考和 `dwy-macos-development` 的弹窗参考；这些 Skill 不可用时查 Apple 官方文档。

依据：[SwiftUI popover](https://developer.apple.com/documentation/swiftui/view/popover(ispresented:attachmentanchor:arrowedge:content:))、[弹层设计指引](https://developer.apple.com/design/human-interface-guidelines/popovers)。
