# macOS 弹窗差异

- 共通锚点规则和验证见 `dwy-swift-development` 的弹层参考。窗口可移动和缩放，检查窗口及入口位置变化后，popover 是否仍指向正确控件。
- Apple 文档说明 SwiftUI popover 的指定 `arrowEdge` 在 macOS 上一直受尊重；系统边界和内容仍须在目标系统实测。若允许系统选择方向，使用不指定边的重载。
- 结合产品交互检查键盘、焦点、取消和点击外部关闭；不要把 iOS 的紧凑尺寸适配行为直接套到 macOS。

## 按钮触发的简短说明

- 问号或信息按钮只用于解释当前功能、字段或操作时，必须在该按钮上挂载 `.popover`。这条规则同样适用于已经打开的 sheet 内的帮助按钮，禁止仅为展示说明再叠一层 `.sheet` 或 `.alert`。
- 说明内容按需提供标题和正文，省去「完成」或「确定」按钮。验证点击弹层外或按 Escape 可收起说明，已打开的管理或编辑面板保持打开。

## 模态弹框必须用原生模态

- 需要独占输入的弹框（编辑、管理、表单、确认、选择）必须用系统模态承载：SwiftUI `.sheet`、`.alert`、`.confirmationDialog`、`.fileImporter`，AppKit `beginSheet` / `runModal`。项目已采用 AppleAppKit 时，确认用 `EAlert`，必须由用户关闭的错误用 `.modifier(EErrorAlert(...))`（先确认锁定版本提供该类型），文件选择用 `EFileDialog`。短暂反馈与页内持续提示按 `dwy-apple-appkit` 的反馈组件选型处理。
- 禁止用 `ZStack`、`.overlay`、透明拦截层或同窗口子视图自绘模态弹框。页内叠加需要自行拦截鼠标、键盘、快捷键、菜单命令、焦点与辅助功能，范围难以完整覆盖，底页误操作风险高。AppleAppKit 0.11.0 已移除 `eWindowOverlay`，不再提供页内模态承载。
- 指向某个入口的轻量编辑用 `popover`；明确设计为非模态、可与主窗口并行操作的面板用 `EToolPanel` / `EToolWindow` 或独立窗口，不伪装成模态。
- AppleAppKit 0.14.0 起，Window 菜单和 Dock 重开共用 `EMainWindow`。给主场景和窗口标记使用同一标识，应用层保留开窗动作。需要用系统热键调前时，应用持有 `MacGlobalHotkey` 注册，并在停用或改绑前释放。
- macOS sheet 附着于所属窗口，系统负责窗口级输入隔离和焦点。不给底页或整窗自绘灰色蒙层、半透明变暗层或背景模糊；系统自身的呈现效果保持原样。
- sheet 的确认按钮使用 `.keyboardShortcut(.defaultAction)`，取消或关闭按钮使用 `.keyboardShortcut(.cancelAction)` 以响应 Escape。尺寸用内容 `.frame` 或 `presentationSizing` 控制，不套用 iPhone detent。多层模态由上一层 sheet 继续呈现，关闭后交还下一层。
- 应用级 `Commands` 在 sheet 显示时仍可能对主窗口生效时，按同一呈现状态禁用会修改底页数据的命令。
- 在目标 macOS 的浅色和深色外观中实际打开弹框，验证底页无法点击和输入、Escape / Return 行为、焦点进入与关闭后恢复。
