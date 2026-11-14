# EPicker

ID: designkit.mac.picker
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.8.0-beta.6

## 用途
通过原生菜单或分段选择强类型或 Optional 值。

## 参数、状态与约束
tag 必须与 Binding 类型匹配。候选移除不自动改选第一项；提供 nil 或明确未匹配状态。示例显示实际选值。

菜单选项图标可选：Label 与 SF Symbol 提供图标，Text 继续显示纯文字。EPicker 仅在 menu 分支应用 titleAndIcon，使 macOS 27 也显式显示所提供的图标，不改变原生勾选、菜单箭头、tag 或 Binding 语义。触发器标题不决定选项是否带图标。分段呈现保留原样，不套用菜单专属的标签样式覆盖。

示例把纯文字 nil 选项、图文选项、带图标的禁用项和动态纯文字项放在同一菜单，均使用稳定 Optional String tag。分段示例保持纯文字；两个控件的实际选值均在下方可见。

示例只持局部 @State，切换组件或重置后恢复。bundle 参数默认 .main；目录显式注入所属资源 bundle，可复制到应用或带资源的 SwiftPM 消费方。预览设置集中在 Playground 顶部弹出层，当前窗口切换组件时保留，仅作用预览子树；系统信息与完整说明/代码默认折叠。

## 验证状态与已知限制
可用：编译示例直接调用公开 API；需宿主能力：窗口、键盘与辅助功能。资源/源码一致性有自动校验；macOS 26 前台交互、IME、VoiceOver、真实材质和跨窗口边缘仍需单独验收，展示状态不代表业务成功。
