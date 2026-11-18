# macOS 平台对话框与窗口

`DesignKitMac` 提供 `EAlert`、`EFileDialog`、`EToolPanel`、`EToolWindow` 和 `ESettingsWindowChrome`。系统适配在 `apple/Sources/macOS/DesignKit/EPlatformDialogs.swift` 与 `apple/Sources/macOS/DesignKit/EWindows.swift` 集中维护。

## 对话框

`EAlert` 接受宿主已解析的标题、说明与操作数组，返回原生 `NSApplication.ModalResponse`。按钮顺序不变；`.destructive` 不绑定 Return，`.cancel` 使用 Escape。表单内容放 `accessoryView`，校验通过 `setActionEnabled(_:at:)` 更新，密码在对话框结束后由宿主清空。

SwiftUI 简单错误提示使用 `.eErrorAlert(title:message:dismissTitle:)`；消息保留到用户关闭，不自动重试或丢弃失败。

## 自定义页内弹框与侧栏

从 AppleAppKit 0.10.0 起，`.eWindowOverlay(isPresented:preferredSize:onDismiss:panel:)` 挂在当前内容区的稳定根视图上。由宿主提供面板样式与内容，容器居中显示并随内容区限位。背景透明，不绘制灰色蒙层或模糊；面板自身的表面、描边和阴影由宿主提供。

AppleAppKit 0.10.1 起的模态行为：

- 显示期间禁用底页的 SwiftUI 控件及其快捷键，并隐藏底页辅助功能入口；控件可呈现平台正常的禁用样式，不给整页加变暗层。透明承载拦截所属窗口内面板之外的点击、滚轮、拖拽与手势，其他独立窗口保持可操作。
- 自动移入面板焦点，Tab / Shift-Tab 只在面板内切换；关闭后恢复仍在同一窗口的原控件，原入口已移除时归还内容区。多层弹框仅最上层处理输入，移除或窗口关闭时清理监听。
- 普通键盘输入发送给面板内的响应者，未处理的普通按键不能传给底页。Command 编辑命令和 SwiftUI `.keyboardShortcut` 保留原生分发，底页快捷键由禁用状态阻断。输入法组合期间优先交给编辑器，普通多行编辑器的 Return 仍用于换行。
- Escape 调用 `onDismiss`，宿主在回调中更新呈现状态；外部点击仅消费，不自动关闭。打开和关闭过渡中以实际承载的存续期保持拦截，面板内开始的鼠标拖拽保留到释放。
- 应用级 `Commands`、显式指定业务 target 的菜单和宿主自行安装的事件监听，不属于页内 SwiftUI 控件树，必须由宿主使用同一呈现状态禁用或在处理入口阻断；例如业务 `Commands` 中的 `Button` 使用 `.disabled(showsOverlay)`。不能假定本地事件监听之间有可依赖的执行顺序，也不通过全局拦截或修改系统菜单强行隔离其他窗口。

必须挂在完整内容区根节点；若只挂在某个按钮或行上，布局尺寸及底页禁用范围都只覆盖该局部。窗口级应用菜单和全局监听需按上述边界配合，不能仅挂修饰符就宣称整个应用已模态化。

在 SwiftUI 原生分栏的侧栏内容上使用 `.ePreventsSidebarCollapse()`，让所属分栏项保持展开。侧栏宽度和工具栏入口仍由宿主管理。

## 文件与目录选择

`EFileDialog.chooseFile` 保留类型过滤，`chooseDirectory` 仅选择目录，两者取消返回 nil。组件只负责系统选择器展示，不读取所选文件、不存书签、不调用 `stopAccessingSecurityScopedResource()`。系统选择器产生的隐式 scope 和后续显式 scope 均由业务原有生命周期管理。

## 窗口宿主

`EToolPanel` 用于工具面板；任务进度面板显式传 `closable: false`，避免关闭窗口被误当任务结束。需要模态参数返回的业务可以继承并自行管理 runModal/stopModal。`EToolWindow` 提供可缩放独立工具窗。内容通过 `setContent` 安装，业务继续持有 delegate、路由及授权。

窗口内容默认接入共享控件主题；语言、locale 和应用主题实例由宿主显式注入。SwiftUI Settings 场景通过 `ESettingsWindowChrome` 在挂载后应用统一标题栏与缩放策略。

## 开发预览

`DesignKitMacPlayground` 的独立 `EPlatformHostPreview()` 可实际打开无写入副作用的确认框、目录选择器与工具面板。也可作为 `EPlayground(projectTitle:)` 的宿主示例内容使用。通用组合的八个展示入口已纳入基础组件目录，并提供中英说明及可复制、已编译的示例。
