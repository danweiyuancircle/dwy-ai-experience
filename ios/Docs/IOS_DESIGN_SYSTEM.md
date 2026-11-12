# iOS 设计规范与组件抽取方案

日期：2026-11-12。状态：第二版设计基线，已补齐 Skill 对照细则；组件实现、迁移和设备验收尚未完成。

完整组件目录与交付标准见 `ios/Docs/UI_FOUNDATION_PLAN.md`；tokens 和配置遵循 `ios/Docs/DESIGN_TOKENS.md`、`ios/Docs/DESIGN_CONFIGURATION.md`。本文件负责 iOS 的平台差异，不重复维护另一份全局 token 表。

## 平台目标

- iOS / iPadOS 18.0 起；基线回归覆盖 iOS 18 和当前最新支持的大版本。iOS 26 是玻璃首次引入节点，相关组件保留该节点的覆盖；与最新版本相同时去重，其他版本仅在有已知差异时增加。
- `DesignKitIOS` 只负责平台 UI。业务配置留调用方；公共语义和现有主题枚举沿用 `DesignCore`。
- iOS 26 用原生 Liquid Glass；iOS 18 使用标准原生样式或已有可读实色设计。可用性判断集中在库内部，不散落业务页面，不把普通模糊伪称玻璃。
- iPhone、iPad、安全区、横竖屏、系统键盘、Dynamic Type、VoiceOver、外接键盘与指针都属于验收范围；不以屏幕尺寸推断只有触摸输入。

## 视觉与交互规范

| 维度 | iOS 约定 |
|---|---|
| 层级 | 内容保持清晰；导航与必要浮动操作使用系统材质，避免把每个列表按钮都玻璃化 |
| 字体 | 正文、说明、标题使用可缩放语义字体，允许多行；不全局复制 Mac 的固定字号 |
| 触点 | 通用主要交互以 44pt 级舒适触点为设计基准，小字形通过外围命中扩展；独立处理布局尺寸与实际触点 |
| 色彩 | 使用动态语义颜色；品牌强调可注入，错误/危险与禁用保持独立语义；ADBox 的蓝色不是库的固定品牌 |
| 布局 | 主操作可按移动端场景全宽；遵循安全区和键盘避让；iPad 不直接放大手机固定卡片 |
| 反馈 | 优先原生交互；按压缩放只用于适合的内容按钮，尊重减少动态效果；玻璃按钮不再叠一套重复按压动画 |
| 触觉 | 封装平台能力，是否启用由应用注入；不读取 ADBox 的 remote.haptics 设置键 |
| 导航 | 返回与关闭保持不同语义；优先原生导航/Sheet，确有自定义需求再使用公共页头 |

44pt 是通用舒适目标，不意味着未经评估把 ADBox 所有冻结尺寸直接改成 44；每个既有入口先核对命中和布局，再迁移。

## 布局与明确验收矩阵

- 布局统一使用 pt。原型基准为 393×852 pt，用来表达布局意图，不写死开发页面宽高。
- 必验宽度为 375 / 393 / 430 pt，分别检查表单、列表、底部固定动作与弹层；同时覆盖长文案和字号放大，不允许关键截断、横向溢出或不可点击。
- 页面优先使用 stack、grid、Spacer、safeAreaInset、容器相对布局；不用 UIScreen.main.bounds 换算主布局，也不用绝对 offset 拼页面。固定比例实体控件允许固定 pt，但外层必须自适应。
- 前景内容遵循安全区；只有背景/适用遮罩延展，不能写死刘海、状态栏或 Home 条高度。键盘出现、旋转与 iPad 尺寸类别变化后，当前字段及提交/取消动作仍须可达。

## 弹层、锚点与当前目标

- 需要指向入口的 popover，及可能呈现为 popover 的 confirmationDialog，关联实际触发按钮或行；不要统一挂在外层 ScrollView 或全局根。记录当前业务对象与来源 scene，列表复用或选择变化不得让确认动作串目标。
- iPhone popover 可适配为 sheet，垂直紧凑环境可全屏；iPad/常规尺寸类别按实际呈现验收，不承诺始终出现箭头。
- 指定 arrowEdge 的行为按实际 SDK 和运行时核对：iOS 18.1 前不依赖指定边被遵循；允许系统选方向时使用不指定边的原生重载。仅对涉及该 API 的组件增加 18.0/18.1 差异测试。
- 验证触发、滚动、边缘、旋转/窗口变化、取消再开、原目标确认与焦点/键盘恢复。编译或起终点截图不能证明锚点和动态过程正确。

## 组件与实际来源

以下 ADBox 路径相对 ADBox 仓库根，目标路径相对基础库仓库根。

| 组件族 | ADBox 当前来源 | 提取与改造边界 |
|---|---|---|
| 操作/图标按钮 | `ios/Sources/Foundation/DesignKit/ButtonStyles.swift`；各页 Button label | 封装原生 Button 的层级、Label、busy、disabled、role；现有 PressStyle 是样式，不是完整按钮 |
| 动作菜单/单选 | `ios/TVRemote/Features/Global/Settings/SettingsView.swift`、`ios/TVRemote/Features/RemoteControl/Apps/AppsView.swift`、`ios/TVRemote/Features/DeviceConnection/ADBGuide/ADBGuideView.swift` | Menu 与 Picker 分开；保留 Binding、tag、禁用项与系统菜单语义，不把动作菜单当选值器 |
| 输入/密码/搜索 | `ios/TVRemote/Features/DeviceConnection/Discover/DeviceEditSheet.swift`、`ios/TVRemote/Features/RemoteControl/Shortcuts/ShortcutsView.swift` 等 | 通用外壳不负责 IP、端口、命令或账号校验；不截断正在组合的中文，不自动改写值 |
| 表单行/设置行 | `ios/TVRemote/Features/Global/Settings/SettingsView.swift` 与编辑表单 | 接收标签、说明、错误与内容槽；保持移动端排版，长文案/错误可换行 |
| 页头/弹层头 | `ios/Sources/Foundation/DesignKit/PageHeaderBar.swift` | 分开返回与关闭 API；补可访问名称、触点和长标题评估，不机械复制当前 30×34 的返回按钮框 |
| 非模态提示 | `ios/Sources/Foundation/DesignKit/ToastView.swift`、`ios/Sources/Foundation/DesignKit/NoticeAlert.swift` | 展示内容与宿主状态分开；覆盖初始消息、替换、取消、销毁和计时；重要失败不靠短暂 toast 承载 |
| 输入弹窗 | `ios/Sources/Foundation/DesignKit/InputDialog.swift` | 只抽可复用呈现和动作；字数上限由业务策略决定，取消标题由应用本地化提供，不依赖应用 loc 单例 |
| 进度遮罩 | `ios/Sources/Foundation/DesignKit/BlockingProgressOverlay.swift` | 显示进度和可选取消动作，不启动任务、不自行设置超时、不把取消显示成成功 |
| 分享/收键盘/触觉 | `ios/Sources/Foundation/DesignKit/ShareSheet.swift`、`ios/Sources/Foundation/DesignKit/KeyboardDismiss.swift`、`ios/Sources/Foundation/DesignKit/Haptics.swift` | UIKit 适配留本端；分享锚点、多 scene、滚动不被手势拦截、偏好注入须验证 |

通用组件落在 `ios/Sources/iOS/DesignKit/`。建议按 Controls、Feedback、Presentation 分组，随着实际抽取创建，不预先铺空目录。

## 不直接复制的内容

- `ios/TVRemote/Features/RemoteControl/Remote/RemoteControls.swift` 的 DPad 依赖 `RemoteKey`，属于 ADBox 遥控业务；可复用的图标按键视觉可用基础按钮表达，方向盘整体不进入通用库。
- `ios/Sources/Foundation/DesignKit/Palette.swift` 的 gold 实际是 ADBox 蓝强调色；保留业务别名兼容，公共主题使用 accent 等语义。
- `ios/Sources/Foundation/DesignKit/ControlTokens.swift` 中已有桌面规格，不能整体作为 iOS 规范搬入库。
- 完整连接页、付费墙、设备信息、文件管理、录屏抓包生命周期及账号状态留业务；认证品牌按钮复用既有认证 UI 产品。

## 接口约束

- `EButton` 保留 LocalizedStringKey / LocalizedStringResource 或 Text/Label builder 的本地化语义，接收 emphasis、原生 role、isBusy、action；用户原文与已解析 String 用明确路径表达，disabled 与 onSubmit 等继续用原生修饰符。
- `EIconAction` 要求明确可访问名称；SF Symbol 与资源图片都可作为 Label，不在库里加载网络图片。
- `EPicker<Selection>` 使用强类型 Binding 和原生选项 builder，不把枚举转换成 String/Any；同一组互斥值由一个选择绑定表达。
- 文本框不擅自 trim、补默认值或保存历史；输入配置、验证和提交由应用负责，密码继续使用 SecureField。
- 组件只负责展示 busy，不执行网络请求或捕获业务异常；购买、权限、设备归属、成功提示的业务判定由调用方负责。
- 所有新 API 发布前以实际抽取用例和独立示例验证；不为了两端命名对称增加无实际职责的 wrapper。

## 实施与验收

1. 提高基础库 iOS 清单、iOS 模板及相关文档到 18.0，保留其他模块已发布接口；iOS 旧兼容版发布策略不在组件库中实现。
2. 先抽按钮、表单和选择，再抽提示及呈现。每类都有公开接口示例、状态表和有意义的交互/边界测试。
3. 建立不依赖 ADBox 的展示 target，运行 iOS 18 与当前最新支持大版本；玻璃组件补充 26 引入节点，按已知差异增加具体版本。覆盖 375/393/430 pt、长文案/Dynamic Type、iPad 弹层锚点、旋转、安全区、键盘、VoiceOver、减少透明度/动态效果和增加对比度。
4. ADBox 本地 wrapper 先薄接公开组件，保留既有业务行为；使用已发布固定版本后再删除被替代实现。不能用最新工作树冒充 ADBox 已锁定版本。
5. iOS 18 验证标准样式和业务可用，26 引入节点及最新支持版本验证相应原生材质与动态过程；均验证输入法、焦点和确认/取消/失败链路，不以截图或构建代替操作。

官方依据：

- [Designing for iOS](https://developer.apple.com/design/human-interface-guidelines/designing-for-ios)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Native controls](https://developer.apple.com/documentation/swiftui/controls-and-indicators)
