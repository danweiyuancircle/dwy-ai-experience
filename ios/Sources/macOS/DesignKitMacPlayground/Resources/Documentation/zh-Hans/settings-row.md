# ESettingsRow

ID: designkit.mac.settings-row
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.8.0-beta.6

## 用途
把标签、说明和原生设置控件放在同一行。

## 参数、状态与约束
窄空间自适应，不固定高度。选择和持久化由宿主负责；行本身不添加点击或导航行为。

示例只持局部 @State，切换组件或重置后恢复。bundle 参数默认 .main；目录显式注入所属资源 bundle，可复制到应用或带资源的 SwiftPM 消费方。预览设置集中在 Playground 顶部弹出层，当前窗口切换组件时保留，仅作用预览子树；系统信息与完整说明/代码默认折叠。

## 验证状态与已知限制
可用：编译示例直接调用公开 API；需宿主能力：窗口、键盘与辅助功能。资源/源码一致性有自动校验；macOS 26 前台交互、IME、VoiceOver、真实材质和跨窗口边缘仍需单独验收，展示状态不代表业务成功。
