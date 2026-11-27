# EButton

ID: designkit.mac.button
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.11.0

## 用途
触发明确操作，保留原生主次、危险、忙碌和禁用语义。

## 能力
- 强调度 — primary、secondary 或 plain，样式随控件层级（内容、工具栏、浮动玻璃）变化。
- 角色 — ButtonRole.destructive 将着色切换为危险色。
- 忙碌 — isBusy 显示小型进度并仅禁用当前按钮。
- 自定义标签 — ViewBuilder 标签可放 SF Symbol 或图片，仅图标时必须提供可访问名称。

## 参数、状态与约束
执行、错误和完成由宿主负责。忙碌仅禁用此按钮；示例只增加局部计数。

示例只持局部 @State，切换组件或重置后恢复。bundle 参数默认 .main；目录显式注入所属资源 bundle，可复制到应用或带资源的 SwiftPM 消费方。预览设置集中在 Playground 顶部弹出层，当前窗口切换组件时保留，仅作用预览子树；系统信息与完整说明/代码默认折叠。

## 验证状态与已知限制
可用：编译示例直接调用公开 API；需宿主能力：窗口、键盘与辅助功能。资源/源码一致性有自动校验；macOS 26 前台交互、IME、VoiceOver、真实材质和跨窗口边缘仍需单独验收，展示状态不代表业务成功。
