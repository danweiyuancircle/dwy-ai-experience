# EStatusBadge

ID: designkit.mac.status-badge
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.8.0-beta.2

## 用途
通过文字和图标展示普通、成功、警告与失败状态。

## 参数、状态与约束
不推断业务成功，也不是按钮。不仅依赖颜色，不把危险色替换成品牌强调色。

示例只持局部 @State，切换组件或重置后恢复。bundle 参数默认 .main；目录显式注入所属资源 bundle，可复制到应用或带资源的 SwiftPM 消费方。预览设置集中在 Playground 顶部弹出层，当前窗口切换组件时保留，仅作用预览子树；系统信息与完整说明/代码默认折叠。

## 验证状态与已知限制
可用：编译示例直接调用公开 API；需宿主能力：窗口、键盘与辅助功能。资源/源码一致性有自动校验；macOS 26 前台交互、IME、VoiceOver、真实材质和跨窗口边缘仍需单独验收，展示状态不代表业务成功。
