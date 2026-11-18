# macOS 平台对话框与窗口

`DesignKitMac` 提供 `EAlert`、`EFileDialog`、`EToolPanel`、`EToolWindow` 和 `ESettingsWindowChrome`。系统适配在 `apple/Sources/macOS/DesignKit/EPlatformDialogs.swift` 与 `apple/Sources/macOS/DesignKit/EWindows.swift` 集中维护。

## 对话框

`EAlert` 接受宿主已解析的标题、说明与操作数组，返回原生 `NSApplication.ModalResponse`。按钮顺序不变；`.destructive` 不绑定 Return，`.cancel` 使用 Escape。表单内容放 `accessoryView`，校验通过 `setActionEnabled(_:at:)` 更新，密码在对话框结束后由宿主清空。

SwiftUI 简单错误提示使用 `.eErrorAlert(title:message:dismissTitle:)`；消息保留到用户关闭，不自动重试或丢弃失败。

## 自定义页内弹框与侧栏

从 AppleAppKit 0.10.0 起，`.eWindowOverlay(isPresented:preferredSize:onDismiss:panel:)` 挂在当前内容区的稳定根视图上。由宿主提供面板样式与内容。容器居中显示并随内容区限位，保持底页原有亮度，拦截内容区背景点击，按 Escape 时调用 `onDismiss`。宿主在回调中更新呈现状态，管理面板的键盘焦点、业务快捷键以及关闭后的焦点归还。工具栏和窗口控制按钮的交互由窗口宿主管理。

在 SwiftUI 原生分栏的侧栏内容上使用 `.ePreventsSidebarCollapse()`，让所属分栏项保持展开。侧栏宽度和工具栏入口仍由宿主管理。

## 文件与目录选择

`EFileDialog.chooseFile` 保留类型过滤，`chooseDirectory` 仅选择目录，两者取消返回 nil。组件只负责系统选择器展示，不读取所选文件、不存书签、不调用 `stopAccessingSecurityScopedResource()`。系统选择器产生的隐式 scope 和后续显式 scope 均由业务原有生命周期管理。

## 窗口宿主

`EToolPanel` 用于工具面板；任务进度面板显式传 `closable: false`，避免关闭窗口被误当任务结束。需要模态参数返回的业务可以继承并自行管理 runModal/stopModal。`EToolWindow` 提供可缩放独立工具窗。内容通过 `setContent` 安装，业务继续持有 delegate、路由及授权。

窗口内容默认接入共享控件主题；语言、locale 和应用主题实例由宿主显式注入。SwiftUI Settings 场景通过 `ESettingsWindowChrome` 在挂载后应用统一标题栏与缩放策略。

## 开发预览

`DesignKitMacPlayground` 的独立 `EPlatformHostPreview()` 可实际打开无写入副作用的确认框、目录选择器与工具面板。也可作为 `EPlayground(projectTitle:)` 的宿主示例内容使用。通用组合的八个展示入口已纳入基础组件目录，并提供中英说明及可复制、已编译的示例。
