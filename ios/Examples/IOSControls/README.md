# iOS 基础组件展示

最低 iOS 18。应用仅消费 `DesignKitIOS` 公开产品，不依赖 ADBox 或 Mac UI。

在仓库根运行：

```sh
DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer xcodegen generate --spec ios/Examples/IOSControls/project.yml
DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer xcodebuild -project ios/Examples/IOSControls/IOSControls.xcodeproj -scheme IOSControls -destination 'platform=iOS Simulator,name=YOUR_EXISTING_SIMULATOR' test
```

将 `YOUR_EXISTING_SIMULATOR` 替换为已有 iOS 18 或更新版本模拟器名称。`IOSControlsTests` 包含 `ios/Tests/DesignKitIOSTests`；macOS 的 `swift test` 不代表这些 UIKit 测试已执行。

展示包含主题、按钮所有层级/角色/忙碌/禁用、菜单、Optional 单选、禁用与动态候选、分段、开关、普通/密码/搜索输入、字段错误、表单动作区、卡片、设置行、标签值、内容状态、状态 badge、持续/短暂提示、定量/不定量进度及取消阶段。数据均保存在展示视图的内存状态中，不调用业务服务。更改系统语言可查看中英文资源。

`IOSControlsUITests` 从实际界面验证：键盘输入保留空白并立即回写绑定、分段切换回写绑定、全宽主按钮左右边缘各仅触发一次。界面上的动作次数和选值来自展示状态，不需要产品调试旁路。

可访问性验证应覆盖长文本、375/393/430pt、辅助字号、横竖屏、iPad、安全区/键盘、VoiceOver、外接键盘、减少透明度/动态效果与增加对比度。浮动按钮在 iOS 26 起采用原生玻璃；其他内容控件保持标准样式。构建与布局测试不能替代输入法、密码 AutoFill、触摸边缘及动态材质的现场验收。

字段继续使用原生 `TextField`/`SecureField`。如需直接配置更复杂编辑器或 FocusState，可把原生编辑器放进 `EFieldShell`/`EField`，不必另写字段外观。宿主拥有键盘收起、提交与取消，组件不替业务校验或 trim 输入。

`ENoticeCenter` 每个宿主独立持有。普通消息持续到主动关闭，只有 `transientSuccess` 默认两秒关闭；读屏、键盘/辅助焦点和触摸停留暂停计时。宿主销毁/消息替换取消旧计时。提示不禁用其他操作；重要错误和需操作的内容使用持久 `EInlineNotice`。

`EProgressValue` 在外部边界拒绝无效值；任务取消请求与真实取消结果分别由业务回写，组件不启动或取消业务任务。
