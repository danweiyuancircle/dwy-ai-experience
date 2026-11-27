import Foundation

/// 组件说明：用途、支持的能力清单、用法约束。每条必须单行且中英文都有，由目录测试检查。
/// 能力项必须能在对应 `apple/Sources/iOS/edesign-kit` 公开 API 中找到依据，不写未实现的愿景。
public struct IOSPlaygroundDocumentation: Sendable {
    public let summary: IOSPlaygroundText
    public let capabilities: [IOSPlaygroundText]
    public let constraints: [IOSPlaygroundText]
}

private func t(_ en: String, _ zh: String) -> IOSPlaygroundText { IOSPlaygroundText(en: en, zh: zh) }

extension IOSPlaygroundComponent {
    public var documentation: IOSPlaygroundDocumentation {
        switch self {
        case .button:
            IOSPlaygroundDocumentation(
                summary: t("Trigger an explicit action with native emphasis, role, busy and disabled semantics.",
                           "用原生层级、角色、忙磌和禁用语义触发明确操作。"),
                capabilities: [
                    t("Emphasis: primary, secondary, tertiary.", "层级：primary、secondary、tertiary。"),
                    t("Native ButtonRole such as destructive uses the danger color.", "原生 ButtonRole（如 destructive）使用危险色。"),
                    t("isBusy shows a progress indicator and blocks repeat taps.", "isBusy 显示进度并阻止重复点击。"),
                    t("Fills the width inside EActionGroup; 44 pt minimum height.", "在 EActionGroup 中铺满宽度；最小高度 44 pt。"),
                    t(".eControlPlacement(.floating) uses native glass on iOS 26+.", ".eControlPlacement(.floating) 在 iOS 26+ 使用原生玻璃样式。"),
                ],
                constraints: [
                    t("The caller owns execution, errors and completion; busy only mirrors external state.",
                      "执行、错误和完成由调用方负责；busy 只反映外部状态。"),
                    t("Use the glass placement only for floating actions, not for content.",
                      "玻璃放置仅用于浮动操作，不用于正文内容。"),
                ])
        case .iconAction:
            IOSPlaygroundDocumentation(
                summary: t("Icon-only action with a mandatory accessibility name.", "必须提供可访问名称的纯图标操作。"),
                capabilities: [
                    t("Icon slot accepts an SF Symbol or a caller resource.", "图标槽支持 SF Symbol 或调用方资源。"),
                    t("Emphasis, role and busy match EButton.", "层级、角色和忙磌与 EButton 一致。"),
                    t("Hit area is at least 44 x 44 pt.", "触点至少 44 x 44 pt。"),
                ],
                constraints: [
                    t("accessibilityLabel is required; never rely on the glyph alone.",
                      "必须传 accessibilityLabel，不能只靠图标表达。"),
                ])
        case .menu:
            IOSPlaygroundDocumentation(
                summary: t("Action menu that keeps native item roles, grouping and disabled semantics.",
                           "保留原生菜单项角色、分组和禁用语义的操作菜单。"),
                capabilities: [
                    t("Menu items are native Button, Divider and role: .destructive.", "菜单项为原生 Button、Divider 和 role: .destructive。"),
                    t("Disabled items stay visible and non-interactive.", "禁用项保持可见且不可点击。"),
                    t("Label closes to a 44 pt tall bordered control.", "标签收起为 44 pt 高的边框控件。"),
                ],
                constraints: [
                    t("Do not nest a Button inside the label; use EPicker for selection instead of actions.",
                      "label 内不要嵌套 Button；选择用 EPicker，不要用菜单。"),
                ])
        case .actionGroup:
            IOSPlaygroundDocumentation(
                summary: t("Vertical action area whose buttons fill the available width.", "纵向动作区，其中按钮铺满可用宽度。"),
                capabilities: [
                    t("Stacks EButton children vertically with the standard control spacing.", "按标准控件间距纵向排列 EButton。"),
                    t("Child buttons expand to full width through the environment.", "子按钮通过环境值铺满宽度。"),
                    t("Works with mixed emphasis, destructive and disabled buttons.", "支持混合层级、危险和禁用按钮。"),
                ],
                constraints: [
                    t("The caller supplies roles and submit/cancel behavior explicitly.", "角色与提交/取消行为由调用方显式提供。"),
                ])
        case .picker:
            IOSPlaygroundDocumentation(
                summary: t("Single selection with menu or segmented presentation.", "菜单或分段呈现的单选。"),
                capabilities: [
                    t("Presentation: .menu or .segmented.", "呈现：.menu 或 .segmented。"),
                    t("Optional selection via a nil tag.", "通过 nil tag 支持 Optional 选择。"),
                    t("Disabled options and dynamically added or removed options.", "支持禁用选项与动态增删候选。"),
                ],
                constraints: [
                    t("It never changes the selection when options change; show your own notice for stale values.",
                      "候选变化时不替调用方改选值，失效值需自行提示。"),
                    t("Each option needs a stable tag whose type matches the selection.", "每个选项需稳定且类型匹配的 tag。"),
                ])
        case .switchControl:
            IOSPlaygroundDocumentation(
                summary: t("Native switch bound to a Boolean, tinted by the brand accent.", "绑定 Boolean 的原生开关，用品牌强调色着色。"),
                capabilities: [
                    t("Accent follows light, dark and increased-contrast pairs.", "强调色跟随明、暗和高对比度配对。"),
                    t("44 pt minimum row height with a localizable label.", "行高至少 44 pt，标签可本地化。"),
                    t("Disabled state through the standard .disabled modifier.", "禁用状态使用标准 .disabled。"),
                ],
                constraints: [
                    t("The binding reflects the user's choice only; background commits are the caller's job.",
                      "绑定只表达用户选择，后台提交由调用方管理。"),
                ])
        case .textField:
            IOSPlaygroundDocumentation(
                summary: t("Single-line native text field inside the shared field shell.", "共享字段外壳中的单行原生文本框。"),
                capabilities: [
                    t("Title and optional prompt are separate Text values.", "标题和可选 prompt 是独立的 Text。"),
                    t("isInvalid draws the danger border.", "isInvalid 绘制危险色边框。"),
                    t("FocusState, submitLabel and onSubmit keep native behavior.", "FocusState、submitLabel 和 onSubmit 保持原生行为。"),
                ],
                constraints: [
                    t("It does not trim, truncate, validate or store history.", "不 trim、截断、校验或保存历史。"),
                ])
        case .secureField:
            IOSPlaygroundDocumentation(
                summary: t("Password input that always uses the native SecureField.", "始终使用原生 SecureField 的密码输入。"),
                capabilities: [
                    t("Keeps secure entry and AutoFill via textContentType.", "通过 textContentType 保留安全输入与 AutoFill。"),
                    t("isInvalid draws the danger border.", "isInvalid 绘制危险色边框。"),
                    t("Same shell, height and typography as ETextField.", "外壳、高度和字体与 ETextField 一致。"),
                ],
                constraints: [
                    t("Never echo or log the bound value; AutoFill needs a real device check.",
                      "不要回显或记录绑定值；AutoFill 需真机验证。"),
                ])
        case .searchField:
            IOSPlaygroundDocumentation(
                summary: t("Search input that reads and writes only the current string.", "只读写当前字符串的搜索输入。"),
                capabilities: [
                    t("Leading magnifier icon hidden from VoiceOver.", "前置放大镜图标对 VoiceOver 隐藏。"),
                    t("Clear button appears only when text is non-empty.", "仅在有文本时显示清空按钮。"),
                    t("Clear button has a 44 pt hit area and a localized name.", "清空按钮触点 44 pt 且有本地化名称。"),
                ],
                constraints: [
                    t("Clearing does not run a request or delete history.", "清空不会发起请求或删除历史。"),
                ])
        case .fieldShell:
            IOSPlaygroundDocumentation(
                summary: t("Visual shell for a native editor you configure yourself.", "供自行配置的原生编辑器使用的视觉外壳。"),
                capabilities: [
                    t("Surface fill with a one-pixel hairline border.", "表面填充加一物理像素发丝边框。"),
                    t("isInvalid switches the border to the danger color.", "isInvalid 将边框切为危险色。"),
                    t("Hosts TextField, SecureField or any native editor.", "可承载 TextField、SecureField 或任意原生编辑器。"),
                ],
                constraints: [
                    t("Composition input and focus stay with the native editor inside.", "组合输入与焦点仍由内部原生编辑器负责。"),
                ])
        case .field:
            IOSPlaygroundDocumentation(
                summary: t("Form field that combines label, editor, hint and error.", "组合标签、编辑器、提示和错误的表单字段。"),
                capabilities: [
                    t("Optional hint text below the editor.", "编辑器下方可选提示文字。"),
                    t("Error text replaces the hint and adds a warning icon.", "错误文字取代提示并带警示图标。"),
                    t("Any editor can be the content slot.", "内容槽可放任意编辑器。"),
                ],
                constraints: [
                    t("Give the inner editor its own accessibility title; the label alone is decorative.",
                      "内部编辑器需有自己的可访问标题，外部标签只是装饰。"),
                    t("It never clears the value or moves focus automatically.", "不自动清值或移动焦点。"),
                ])
        case .form:
            IOSPlaygroundDocumentation(
                summary: t("Scrolling form container with adaptive page insets.", "带自适应页边距的滚动表单容器。"),
                capabilities: [
                    t("Insets are 16 pt compact and 24 pt regular.", "页边距 compact 16 pt、regular 24 pt。"),
                    t("Keyboard dismisses interactively when scrolling.", "滚动时键盘可交互收起。"),
                    t("Uses the grouped background and standard section spacing.", "使用分组背景和标准分区间距。"),
                ],
                constraints: [
                    t("Do not give it a fixed height; the host owns FocusState and keyboard toolbar.",
                      "不要固定高度；FocusState 与键盘工具栏由宿主负责。"),
                ])
        case .card:
            IOSPlaygroundDocumentation(
                summary: t("Opaque content card with a dynamic surface and hairline border.", "不透明的内容卡，动态表面色加发丝边框。"),
                capabilities: [
                    t("Standard card inset and 16 pt corner radius.", "标准卡片内边距与 16 pt 圆角。"),
                    t("Follows light, dark and increased contrast.", "随明、暗和高对比度变化。"),
                    t("Any content slot, full width.", "任意内容槽，铺满宽度。"),
                ],
                constraints: [
                    t("Body content is never glassified; cards do not own navigation.", "正文不玻璃化；卡片不负责导航。"),
                ])
        case .settingsRow:
            IOSPlaygroundDocumentation(
                summary: t("Settings row with label, optional detail and a trailing control.", "带标签、可选说明和尾部控件的设置行。"),
                capabilities: [
                    t("Horizontal layout at normal text sizes.", "正常字号下水平排列。"),
                    t("Switches to vertical layout at accessibility text sizes.", "辅助功能字号下切换为纵向。"),
                    t("Optional secondary detail text.", "可选的次级说明文字。"),
                ],
                constraints: [
                    t("It adds no navigation or tap gesture; the trailing control handles input.",
                      "不附加导航或点击手势，由尾部控件处理输入。"),
                ])
        case .labelValue:
            IOSPlaygroundDocumentation(
                summary: t("Read-only label and value pair.", "只读的标签与值。"),
                capabilities: [
                    t("Value text is selectable.", "值文字可选择。"),
                    t("Long values wrap and keep line breaks.", "长值自动换行并保留换行符。"),
                    t("Secondary caption style for the label.", "标签使用次级说明样式。"),
                ],
                constraints: [
                    t("Pass user text with Text(verbatim:) so it is not looked up as a localization key.",
                      "用户原文用 Text(verbatim:)，避免被当作本地化 key。"),
                ])
        case .statusBadge:
            IOSPlaygroundDocumentation(
                summary: t("Non-interactive status tag with icon and text.", "带图标和文字的非交互状态标签。"),
                capabilities: [
                    t("Tones: neutral, success, warning, error.", "语气：neutral、success、warning、error。"),
                    t("Icon and text both convey status, never color alone.", "图标与文字同时表达状态，不只靠颜色。"),
                    t("Long text wraps.", "长文案可换行。"),
                ],
                constraints: [
                    t("Status colors are independent from the brand accent.", "状态色与品牌强调色相互独立。"),
                ])
        case .stateView:
            IOSPlaygroundDocumentation(
                summary: t("Placeholder for idle, loading, success, empty and failure content.", "用于空闲、加载、成功、空和失败内容的占位。"),
                capabilities: [
                    t("Five explicit EContentState values with matching icons.", "五种显式 EContentState 及对应图标。"),
                    t("Loading shows a progress indicator.", "加载状态显示进度指示。"),
                    t("Optional detail and an actions slot.", "可选说明文字和操作槽。"),
                ],
                constraints: [
                    t("State must come from the business layer; an empty collection is never read as success.",
                      "状态由业务层明确提供，空集合不会被推断为成功。"),
                    t("Retry actions are supplied by the caller; nothing retries automatically.",
                      "重试操作由调用方提供，不自动重试。"),
                ])
        case .noticeHost:
            IOSPlaygroundDocumentation(
                summary: t("Non-modal notice host driven by an ENoticeCenter.", "由 ENoticeCenter 驱动的非模态提示宿主。"),
                capabilities: [
                    t("Persistent notices render as an inline notice with a dismiss button.", "持久消息显示为带关闭按钮的内联提示。"),
                    t("Transient messages render as a compact toast and auto-dismiss.", "短暂消息显示为紧凑 toast 并自动消失。"),
                    t("VoiceOver announces messages and pauses the timer.", "VoiceOver 会播报消息并暂停计时。"),
                    t("Actions slot for persistent notices.", "持久提示可带操作槽。"),
                ],
                constraints: [
                    t("One center per host; place it in safeAreaInset and call cancelPendingDismissal when it disappears.",
                      "一个 center 对应一个宿主，建议放在 safeAreaInset。"),
                ])
        case .toast:
            IOSPlaygroundDocumentation(
                summary: t("Compact short feedback drawn by itself.", "自行绘制的紧凑短反馈。"),
                capabilities: [
                    t("Tone-driven default icon or a custom SF Symbol.", "默认按语气选图标，也可自定义 SF Symbol。"),
                    t("Long text wraps and the toast grows in height.", "长文案换行并增高。"),
                    t("Combined into one accessibility element.", "合并为一个可访问元素。"),
                ],
                constraints: [
                    t("Used directly, the host owns placement and when it disappears.", "直接使用时位置与消失时机由宿主管理。"),
                ])
        case .inlineNotice:
            IOSPlaygroundDocumentation(
                summary: t("Persistent inline notice that can carry explicit actions.", "可带明确操作的持久内联提示。"),
                capabilities: [
                    t("Tones with matching icons.", "带对应图标的语气。"),
                    t("Actions share the row when they fit, otherwise move below.", "操作能放下时同行，否则换到下方。"),
                    t("Accessibility text sizes always use the stacked layout.", "辅助功能字号始终用纵向布局。"),
                ],
                constraints: [
                    t("No timer and no modal overlay; use it for errors that need a decision.",
                      "无计时也无模态蒙层，适合需要用户决定的错误。"),
                ])
        case .taskProgress:
            IOSPlaygroundDocumentation(
                summary: t("Task progress with optional determinate value and cancel action.", "带可选定量值和取消操作的任务进度。"),
                capabilities: [
                    t("Determinate progress via a validated EProgressValue.", "通过已校验的 EProgressValue 展示定量进度。"),
                    t("Indeterminate when progress is nil.", "progress 为 nil 时不定量。"),
                    t("Phases: running, cancelling, cancelled, succeeded, failed.", "阶段：running、cancelling、cancelled、succeeded、failed。"),
                    t("Cancel button only while running.", "取消按钮仅在 running 时显示。"),
                ],
                constraints: [
                    t("EProgressValue rejects NaN, infinity and out-of-range fractions; handle the thrown error.",
                      "EProgressValue 拒绝 NaN、无穷和越界值，需处理抛出的错误。"),
                    t("The component never starts or cancels work; a cancel request is not a cancelled result.",
                      "组件不启动或取消任务；取消请求不等于已取消。"),
                ])
        case .alert:
            IOSPlaygroundDocumentation(
                summary: t("Single-button native alert mounted with .modifier.", "用 .modifier 挂载的单按钮原生提示框。"),
                capabilities: [
                    t("Title, message and dismiss title are host Text values.", "标题、消息和关闭文案由宿主提供。"),
                    t("Closing writes false back to the presentation binding.", "关闭时将 false 写回呈现绑定。"),
                    t("Native alert accessibility and focus handling.", "原生提示框的可访问性与焦点处理。"),
                ],
                constraints: [
                    t("Mount it on a view in the current scene; only one alert can show at a time.",
                      "挂在当前 scene 的视图上，同一时刻只能显示一个。"),
                ])
        case .confirm:
            IOSPlaygroundDocumentation(
                summary: t("Native confirmation alert with cancel and confirm.", "带取消和确认的原生确认框。"),
                capabilities: [
                    t("Cancel runs no business action.", "取消不执行任何业务动作。"),
                    t("isDestructive marks the confirm button as destructive.", "isDestructive 将确认按钮标为危险。"),
                    t("onConfirm only reports the user's intent.", "onConfirm 只表达用户意图。"),
                ],
                constraints: [
                    t("Capture the business target when opening so a selection change cannot redirect the confirm.",
                      "打开时固定业务目标，避免选择变化后确认到另一对象。"),
                ])
        case .errorAlert:
            IOSPlaygroundDocumentation(
                summary: t("Native error alert driven by an optional message.", "由可选消息驱动的原生错误提示。"),
                capabilities: [
                    t("Shown whenever the message binding is non-nil.", "消息绑定非 nil 时即显示。"),
                    t("Message is displayed verbatim.", "消息按原文显示。"),
                    t("Dismissing clears the binding to nil.", "关闭时把绑定清为 nil。"),
                ],
                constraints: [
                    t("No auto-dismiss and no implicit retry; do not pass secrets or raw server payloads.",
                      "不自动消失、不隐式重试；不要传入密钥或原始服务端负载。"),
                ])
        }
    }
}
