# SwiftUI 共享动效方案

> 实施更新：本方案已获授权实施。现已提供 EMotionPreset、eMotion、eTransition 和减少动态效果处理，新增 4 项测试与双平台示例。下文保留设计背景，实际 API、使用约束与本地联调边界以 `ios/Docs/MOTION.md` 为准。接入顺序按后续指示调整为 ADBox 动效与 RightFlow 共享 macOS UI。

## 目标

在现有 DesignCore 中补齐可直接调用的动效能力，让 iOS 与 macOS 项目复用统一的动效节奏、减少动态效果处理和转场规则。实现使用原生 SwiftUI，保持当前 iOS 18、macOS 26 平台下限，不新增运行时依赖。

RightFlow 的侧栏品牌单独处理：只保留真实应用 Logo，48 pt，水平居中；不把应用品牌布局封装进通用动效模块。

## 已有能力

- `ios/Sources/Shared/DesignCore/Motion.swift` 已导出 `Motion.spring`、`press`、`snappy`、`soft`、`page`、`overlay`，以及 `ScalePressButtonStyle` 和 `.scalePress()`。
- 按压样式已读取系统的减少动态效果设置，开启时保留透明度反馈、取消缩放。
- `DesignKitIOS` 和 `DesignKitMac` 已依赖 `DesignCore`。共享层不含 UIKit、AppKit；具体平台组件分别维护。
- RightFlow 已通过 AppleAppKit 版本依赖使用 DesignCore，但当前菜单配置与预览主要直接更新状态，尚未使用统一的显式动效入口。

## 建议落点

继续扩展 `DesignCore`，不再创建一个独立 MotionKit 包。保留现有 Motion 静态属性与 `.scalePress()`，避免破坏现有调用方。

第一批封装三类稳定、已有真实使用场景的能力；以下 API 已实现：

| 能力 | 提议调用方式 | 用途 |
| --- | --- | --- |
| 状态变化动画 | `.eMotion(.selection, value: selection)` | 选中态、悬停、进度或状态的平滑变化；只监听调用方明确传入的值 |
| 列表变化动画 | `.eMotion(.reorder, value: orderedIDs)` | 增删和排序后的自然移动；需要调用方提供稳定行标识 |
| 内容转场 | `.eTransition(.fade)` 或 `.eTransition(.softMove)` | 短暂淡入淡出，或淡入配合小幅位移；不使用出现时延迟隐藏内容 |

`.selection`、`.hover`、`.reorder`、`.page`、`.feedback` 等语义由小型预设类型统一映射到现有 Motion 参数。不是为每个效果再建一套动画实现，也不允许业务页面散落不同的弹簧常量。

`.scalePress()` 继续用于自绘按钮，并补上减少动态效果处理。系统按钮、开关、分段选择器、sheet 和 popover 保留平台自带反馈，不重复叠加通用按压缩放。

SF Symbols 的一次性状态反馈优先直接使用原生 symbolEffect；有第二个确定重复场景时再考虑增加专用语义入口。

## 行为约束

1. 自动读取 `accessibilityReduceMotion`；减少动态效果时关闭动画，位移转场声明降为 opacity，不自行驱动淡入淡出。
2. 动画不负责执行、延迟或重复业务操作，不改变数据写入时机。
3. 快速切换与连续排序使用 SwiftUI 原生可中断动画，不排队重播、不创建常驻 Timer。
4. 通用接口不绑定 RightFlow 的菜单、授权、购买状态或颜色。悬停是否高亮及使用什么颜色由宿主决定。
5. 动画只加在变化区域，不在根 NavigationSplitView 对全部状态变化统一套动画；语言、窗口尺寸和表单输入不被连带动画化。
6. 静态 Logo 不循环呼吸、旋转或弹跳；系统提供的 Liquid Glass 控件反馈不重复实现。
7. 新入口读取系统环境自行处理可访问性；已有直接使用 `Motion.*` 的调用保持兼容，后续按实际场景逐步迁移。

## 文件与验证范围

- 扩展 `ios/Sources/Shared/DesignCore/Motion.swift`，按职责需要将 ViewModifier 拆到同目录，保持公开入口少而明确。
- 新建 `ios/Tests/DesignCoreTests`，在根 `Package.swift` 注册测试目标；验证预设映射、减少动态效果策略以及原 API 兼容性，同步测试用例索引。
- 在 `ios/Examples/Motion` 提供同源双平台示例，覆盖悬停、列表重排和反馈转场；显示真实系统减少动态效果设置，不覆盖只读环境值。
- 补充 iOS 示例与模拟器验收；分别检查触控、macOS 指针/键盘、减少动态效果、快速重复切换和页面销毁后的取消。
- 文档落在 `ios/Docs`，记录 iOS/macOS 的调用方式、适用场景和系统控件无需重复添加的情况。

## 接入顺序

1. 先在共享库完成最小 API、测试、跨平台编译及示例。
2. 按用户后续指示，ADBox 先接入 Mac 设备卡悬停及提示条；iOS 保留已有 Motion 调用，避免覆盖并行修改。RightFlow 接入已有 macOS UI，侧栏居中 48 pt Logo。
3. 用真实配置验证动效没有干扰拖放落点、焦点、滚动位置及预览实时性，再扩展到其他确有需要的页面。
4. 基础库版本发布、标签及消费方依赖升级作为后续交付步骤单独执行；方案评审不等于已授权发布，也不改写已发布标签。

当前状态：已实现基础库 API、测试和示例，并完成消费方源码接入；正式版本尚未发布，正式依赖和锁文件保持原状。
