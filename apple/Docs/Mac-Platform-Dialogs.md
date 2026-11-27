# macOS 平台对话框与窗口

`DesignKitMac` 提供 `EAlert`、`EFileDialog`、`EToolPanel`、`EToolWindow` 和 `ESettingsWindowChrome`。系统适配在 `apple/Sources/macOS/edesign-kit/EPlatformDialogs.swift` 与 `apple/Sources/macOS/edesign-kit/EWindows.swift` 集中维护。

## 对话框

`EAlert` 接受宿主已解析的标题、说明与操作数组，返回原生 `NSApplication.ModalResponse`。按钮顺序不变；`.destructive` 不绑定 Return，`.cancel` 使用 Escape。表单内容放 `accessoryView`，校验通过 `setActionEnabled(_:at:)` 更新，密码在对话框结束后由宿主清空。

SwiftUI 错误弹框使用 `.modifier(EErrorAlert(title:message:dismissTitle:))`。传入非 nil 消息后显示原生弹框，关闭时清空绑定，重试由业务另行发起。

## 模态弹框与侧栏

需要独占输入的弹框使用系统模态：SwiftUI `.sheet`、`.alert`、`.confirmationDialog`，或 AppKit `beginSheet` / `runModal`。macOS sheet 附着在所属窗口上，系统负责窗口级输入隔离、焦点和辅助功能；确认按钮用 `.keyboardShortcut(.defaultAction)`，取消按钮用 `.keyboardShortcut(.cancelAction)`。应用级 `Commands` 中会修改底页数据的命令，由宿主按同一呈现状态禁用。

不用 overlay、ZStack 或透明拦截层在内容区叠加模拟模态。AppleAppKit 0.10.0 / 0.10.1 的 `eWindowOverlay` 已在 0.11.0 移除：页内叠加须自行拦截鼠标、键盘、快捷键、菜单与焦点，范围难以完整覆盖。迁移时把面板内容放入 `.sheet`，删除宿主为页内弹框补的菜单阻断与事件监听。

在 SwiftUI 原生分栏的侧栏内容上使用 `.ePreventsSidebarCollapse()`，让所属分栏项保持展开。侧栏宽度和工具栏入口仍由宿主管理。

## 文件与目录选择

`EFileDialog.chooseFile` 保留类型过滤，`chooseDirectory` 仅选择目录，两者取消返回 nil。组件只负责系统选择器展示，不读取所选文件、不存书签、不调用 `stopAccessingSecurityScopedResource()`。系统选择器产生的隐式 scope 和后续显式 scope 均由业务原有生命周期管理。

## 窗口宿主

`EToolPanel` 用于工具面板；任务进度面板显式传 `closable: false`，避免关闭窗口被误当任务结束。需要模态参数返回的业务可以继承并自行管理 runModal/stopModal。`EToolWindow` 提供可缩放独立工具窗。内容通过 `setContent` 安装，业务继续持有 delegate、路由及授权。

窗口内容默认接入共享控件主题；语言、locale 和应用主题实例由宿主显式注入。SwiftUI Settings 场景通过 `ESettingsWindowChrome` 在挂载后应用统一标题栏与缩放策略。

`EMainWindow(id:)` 统一 Window 菜单和 Dock 的主窗恢复。SwiftUI 场景使用同一个 ID，并把 `main.marker` 放进场景内容的 `.background`。AppKit 宿主直接设置目标窗的 `identifier = main.identifier`。显式菜单入口调用 `main.show { openWindow(id: sceneID) }`，优先调前同 ID 的非最小化窗口，其次恢复已最小化窗口，最后由宿主新建。工具窗和设置窗使用各自的标识。

要接管 Dock 重开，在宿主的 `NSApplicationDelegate.applicationShouldHandleReopen(_:hasVisibleWindows:)` 中返回 `main.handleDockReopen(in: sender, hasVisibleWindows: flag, open: openMain)`。宿主须在主场景挂载时保存可用的开窗动作，使动作在旧窗关闭后仍可调用。仍有可见窗时由 AppKit 处理激活。

## 开发预览

`DesignKitMacPlayground` 的独立 `EPlatformHostPreview()` 可实际打开无写入副作用的确认框、目录选择器与工具面板。也可作为 `EPlayground(projectTitle:)` 的宿主示例内容使用。通用组合的八个展示入口已纳入基础组件目录，并提供中英说明及可复制、已编译的示例。
