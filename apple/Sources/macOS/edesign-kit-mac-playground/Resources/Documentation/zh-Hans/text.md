# EText

ID: designkit.mac.text
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.11.0

## 用途
按语义角色（正文、次要、脚注、标题、分组标题、页面标题、等宽）展示文本，取代裸写系统字体与 .secondary。

## 能力
- 七种角色 — body、secondary、caption、title、sectionTitle、pageTitle、monospaced。
- 语义色覆盖 — tone（EStatusTone）覆盖角色颜色，用于状态文字。
- 修饰符形式 — .eText(_:tone:) 可套在 Label 或任意视图上。
- 三种初始化 — Text、LocalizedStringResource 和 verbatim。

## 参数、状态与约束
字体读 ETypography，颜色读 ESemanticColors，均来自注入的 eControlTheme。tone 复用 EStatusTone 并覆盖角色颜色，状态仍须配有可读文字。.eText(_:tone:) 可用于 Label 等任意视图。

示例只持局部 @State，切换组件或重置后恢复。bundle 参数默认 .main；目录显式注入所属资源 bundle，可复制到应用或带资源的 SwiftPM 消费方。预览设置集中在 Playground 顶部弹出层，当前窗口切换组件时保留，仅作用预览子树；系统信息与完整说明/代码默认折叠。

## 验证状态与已知限制
可用：编译示例直接调用公开 API；需宿主能力：窗口、键盘与辅助功能。资源/源码一致性有自动校验；macOS 26 前台交互、IME、VoiceOver、真实材质和跨窗口边缘仍需单独验收，展示状态不代表业务成功。
