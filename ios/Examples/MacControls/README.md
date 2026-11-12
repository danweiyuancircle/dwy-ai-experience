# DesignKitMac 独立展示

最低 macOS 26、Apple Silicon；通过可选公开产品 `DesignKitMacPlayground` 展示 `DesignKitMac`，不引用 ADBox。由根 `Package.swift` 的 `MacControlsGallery` executable target 构建。

入口仅装配 `EPlayground()`。目录逐项展示全部 22 个可视组件，支持检索、状态预览、局部明暗/语言/字号覆盖，提供双语用途、调用约束与可复制 Swift。局部覆盖不写应用偏好。维护入口与同源校验见 `ios/Sources/macOS/DesignKitMacPlayground/README.md`。

可本地化文字传 `LocalizedStringResource`；原文传 `Text(verbatim:)`，组合框动态原文标题使用 `EComboBox(verbatim:text:suggestions:onEditingEnded:onCommit:)`。资源属于消费项目时在资源上明确 bundle；库不读取 ADBox 本地化单例。

建议输入采用 `NSComboBox`，显式 `completes=false`，弹出窗口/滚动/屏幕定位/辅助功能由 AppKit 管理；输入只更新绑定，失焦回调与显式提交分开。候选变动不写业务历史。上下键循环、中文输入法候选优先、Esc保留原文、鼠标选择仅提交一次，以及窗口上下边缘/ScrollView内弹出仍需前台交互验收；离屏单元测试不证明这些行为。

`EToast` 仅用于非关键成功消息，初始非空和新 id 都启动展示。普通状态两秒后关闭；悬停、可访问焦点、VoiceOver期间保留，带明确关闭动作。错误与需要操作的信息使用持久 `ENotice`。任务进度必须先通过 `EProgressFraction` 校验，非法外部值由业务转成错误，不显示伪造百分比。

当前定向测试覆盖原生配置、输入/提交/失焦边界、候选稳定性、长文案、四种外观的静态品牌对比、进度边界、提示生命周期策略与带插值的独立资源bundle/locale。macOS 26 运行、真实 VoiceOver、输入法、屏幕边缘、颜色合成与完整示例 GUI 验收仍需单独记录。
