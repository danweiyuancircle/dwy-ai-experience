# EComboBox

ID: designkit.mac.combo-box
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.11.0

## 用途
用原生 NSComboBox 建议编辑原文并明确提交。

## 能力
- 可编辑候选 — 原生组合框，支持自由输入和候选列表。
- 提交语义 — 只有提交才调用 onCommit，取消、关闭和失焦都不调用。
- 可选焦点绑定 — isFocused 向调用方暴露焦点。
- 原文标题 — init(verbatim:) 用于不能当作本地化 key 的运行时字符串。

## 参数、状态与约束
候选为按文本去重的原文。同名不同对象用强类型 Picker。编辑结束不等于提交；输入法、键盘和弹出边缘需要前台验收。

示例只持局部 @State，切换组件或重置后恢复。bundle 参数默认 .main；目录显式注入所属资源 bundle，可复制到应用或带资源的 SwiftPM 消费方。预览设置集中在 Playground 顶部弹出层，当前窗口切换组件时保留，仅作用预览子树；系统信息与完整说明/代码默认折叠。

## 验证状态与已知限制
可用：编译示例直接调用公开 API；需宿主能力：窗口、键盘与辅助功能。资源/源码一致性有自动校验；macOS 26 前台交互、IME、VoiceOver、真实材质和跨窗口边缘仍需单独验收，展示状态不代表业务成功。

原生 ComboBox 使用 EControlTheme.typography.nativeBodySize。本页放大预览同时更新该原生字号与 SwiftUI 正文排版。实际字形度量、输入法组合与焦点仍须前台验证。
