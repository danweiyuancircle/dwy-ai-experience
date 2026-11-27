# EIconAction

ID: designkit.mac.icon-action
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.11.0

## 用途
上下文明确时使用有可访问名称的图标操作。

## 能力
- 符号或自定义图标 — 支持 systemImage、ViewBuilder 图标以及 Text 标题加图标。
- 角色与忙碌 — destructive 角色和 isBusy 与 EButton 一致。
- 可访问名称 — 必填 title 作为辅助功能名称，界面上只显示图标。

## 参数、状态与约束
必须提供可读的 VoiceOver/help 名称。SF Symbols 与自定义图片标签由调用方提供。

示例只持局部 @State，切换组件或重置后恢复。bundle 参数默认 .main；目录显式注入所属资源 bundle，可复制到应用或带资源的 SwiftPM 消费方。预览设置集中在 Playground 顶部弹出层，当前窗口切换组件时保留，仅作用预览子树；系统信息与完整说明/代码默认折叠。

## 验证状态与已知限制
可用：编译示例直接调用公开 API；需宿主能力：窗口、键盘与辅助功能。资源/源码一致性有自动校验；macOS 26 前台交互、IME、VoiceOver、真实材质和跨窗口边缘仍需单独验收，展示状态不代表业务成功。
