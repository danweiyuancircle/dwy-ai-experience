# EMenu

ID: designkit.mac.menu
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.8.0-beta.6

## 用途
展示动作、分组条目和原生菜单勾选。

## 参数、状态与约束
打开或取消菜单不执行动作。触发标签内不嵌套 Button，不把动作菜单替代 Picker。

图标由调用方按需提供：带图标的原生 Button 使用 Label 与 SF Symbol，纯文字项使用 Text。EMenu 在原生 Menu 上应用 titleAndIcon 作为默认标签策略，使 macOS 27 中调用方提供的 Label 图标（含分组和子菜单条目）保持显示；不会给 Text 凭空补图标。触发器按调用方的 Label 或 Text 展示，也可用更局部的 labelStyle（如 iconOnly）覆盖。触发器和条目标签互相独立：纯文字触发器可以打开图文条目，图文触发器也可以打开纯文字条目。系统勾选、Toggle 状态、子菜单箭头、禁用与危险角色均保留原生行为。

示例有三个触发器：纯文字菜单、纯文字触发但选项带图标的菜单，以及图文触发的分组混合菜单。混合菜单还包含 Toggle、子菜单、禁用和危险操作。稳定触发 ID 分别以 menu.text-only、menu.with-icons、menu.trigger 结尾；动作只更新可见局部计数或布尔 Binding。

示例只持局部 @State，切换组件或重置后恢复。bundle 参数默认 .main；目录显式注入所属资源 bundle，可复制到应用或带资源的 SwiftPM 消费方。预览设置集中在 Playground 顶部弹出层，当前窗口切换组件时保留，仅作用预览子树；系统信息与完整说明/代码默认折叠。

## 验证状态与已知限制
可用：编译示例直接调用公开 API；需宿主能力：窗口、键盘与辅助功能。资源/源码一致性有自动校验；macOS 26 前台交互、IME、VoiceOver、真实材质和跨窗口边缘仍需单独验收，展示状态不代表业务成功。
