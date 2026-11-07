# macOS 弹窗差异

- 共通锚点规则和验证见 `dwy-swift-development` 的弹层参考。窗口可移动和缩放，检查窗口及入口位置变化后，popover 是否仍指向正确控件。
- Apple 文档说明 SwiftUI popover 的指定 `arrowEdge` 在 macOS 上一直受尊重；系统边界和内容仍须在目标系统实测。若允许系统选择方向，使用不指定边的重载。
- 结合产品交互检查键盘、焦点、取消和点击外部关闭；不要把 iOS 的紧凑尺寸适配行为直接套到 macOS。
