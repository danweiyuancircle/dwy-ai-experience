# 模板生成回归

## 权限模块

`PermissionCoreTests` 的 10 项测试覆盖拒绝不再申请、跨实例同范围请求合并、重复完成回调、limited/restricted/provisional/ephemeral/unknown/unsupported 保真、失败后可重试、预先取消不触发请求、等待期间取消不能返回成功、只写范围显式升级、文件 scope 异常释放与容器 URL 不需 scope，以及随包 MIT 声明。

`LocalNetworkAccessTests` 覆盖系统明确拒绝、首次弹框保活、握手中不被短超时结束、宽限期后拒绝、普通网络错误不误判、waiting/failed 下端口明确拒绝允许恢复、未知网络失败不触发重试、取消与无效端口。

`PermissionMacTests` 的 5 项测试覆盖 FDA/本地网络无法宣称全局已授权、原生受限和只写状态保留、仅引导项不伪造申请成功、同控制器切换权限关闭旧悬浮引导、设置跳转失败关闭引导并清空当前页。打开设置被注入函数替代，不操作真实系统设置。

`PermissionIOSTests` 的 5 项测试在 iOS Simulator 验证按需产品可导入、范围 id 不混用、缺失用途文案先报错、生物识别拒绝空白 reason、provisional 通知可显式升级，以及 whenInUse 到 always 升级在授权不变时不永久等待。定位 manager 与文案校验注入测试实现，不实际触发授权。

根目录执行 `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer swift test --filter Permission`；iOS 需在包含权限测试的 Xcode scheme 中运行 `PermissionCoreTests` 与 `PermissionIOSTests`。macOS 条件编译通过不代表 iOS 测试已运行。CI 的 macOS 测试和 iOS 18 Simulator SDK 交叉构建已包含新增权限产品；真实系统弹框、设置跳转、VoiceOver 和签名沙盒仍需宿主验收。

## 四层模板与架构检查

从统一仓库根执行 `APPLE_TEMPLATE_TOOL_TESTS=1 python3 -B -m unittest discover -s apple/Tests -p 'test_*.py'`，包含真实 XcodeGen 和生成物架构检查；不设该环境变量时只跳过该项工具集成测试。使用现有 Python 3、Swift 和 XcodeGen；原生 CLI 负责读取工程/清单，不解析远端依赖或执行真实购买。

| 用例 | 实际边界 |
| --- | --- |
| `test_ios_template_uses_four_layers` | 真实生成 ios 与单一产品核心包；确认版本、平台产品、根主题、目录替换和 UI 产品使用，不生成 macos 或空 Foundation。 |
| `test_macos_template_uses_four_layers` | 真实生成 macos 与产品核心；核对 macOS 26、arm64、产品链接与主题，不生成 ios。 |
| `test_apple_template_shares_one_business_core` | 双端同时生成并引用同一产品核心；独立 Bundle Identifier，保留四层职责，不复制业务核心。 |
| `test_repository_root_override_locates_templates` | 显式传统一仓库根给 `--skeleton`，应找到 `apple/Templates`。 |
| `test_add_platform_preserves_existing_sources_and_version` | 从单端追加另一端，保留旧端源码和核心清单；新端沿用已有基础库版本，不覆盖已存在目标。 |
| `test_add_platform_rejects_existing_version_disagreement` | 既有平台与业务核心版本声明冲突时，在写入新平台前拒绝操作。 |
| `test_rejects_invalid_arguments_and_existing_destinations` | 无效平台、产品类型标识、Bundle Identifier、缺失参数和已有输出拒绝写入，不覆盖原内容。 |
| `test_ui_boundary_allows_only_registered_business_material` | 材质未登记拒绝；登记具体 BusinessUI 文件后通过，平台依赖检查不豁免，页面加入清单也不得放行。 |
| `test_generated_projects_include_business_ui_and_pass_architecture` | 真实 XcodeGen 生成，业务组件进入各端 Sources，并运行生成物架构检查。 |

`apple/Tests/test_architecture.py` 在临时生成物中注入实际越界；所有修改和锁文件均在临时目录，不读取或修改真实 App 的状态。

| 架构用例 | 实际边界 |
| --- | --- |
| `test_single_and_dual_platform_projects_pass` | 单端、双端的正常生成物通过检查。 |
| `test_core_cannot_import_ui`、`test_core_manifest_cannot_depend_on_ui` | 共享业务核心的源码 import 与 manifest UI 依赖均拒绝。 |
| `test_project_cannot_compile_other_platform_sources`、`test_project_cannot_compile_shared_package_sources` | App sources 不编译另一端或共享包源码。 |
| `test_app_cannot_link_other_platform_ui_product`、`test_app_cannot_reference_other_platform_package` | 平台 UI 产品和本地平台包不能跨端链接。 |
| `test_business_ui_must_be_in_app_sources` | 有业务 UI 实现时必须进入本端 sources，不能只有目录。 |
| `test_excluded_business_ui_is_not_counted_as_compiled` | 真实 XcodeGen 排除业务组件后，检查器必须报告该文件漏编译；excludes 按 source 目录相对路径处理。 |
| `test_source_includes_do_not_hide_missing_business_ui` | XcodeGen 只包含指定文件时，未包含的业务组件不能被误判为已编译。 |
| `test_platform_sources_must_have_an_owner`、`test_platform_sources_can_be_compiled_by_app`、`test_platform_sources_can_be_compiled_by_package`、`test_platform_sources_cannot_be_compiled_twice` | 平台实现必须由 App 或 package 唯一收录；两种合法方式通过，漏编译与重复编译拒绝。 |
| `test_platform_target_can_be_transitively_linked` | App 经同包产品传递连接平台 target 时仍识别真实编译归属，不要求重复直接链接。 |
| `test_package_targets_cannot_compile_same_source` | 不同 package targets 不能重复收录同一 Swift 实现。 |
| `test_package_target_cannot_compile_other_platform` | package target 不能把另一端实现纳入源码。 |
| `test_versions_must_match_between_manifests_and_projects`、`test_apple_appkit_must_use_exact_version` | 同一外部依赖多处声明保持一致，AppleAppKit 必须精确锁定。 |
| `test_lock_version_must_match_exact_requirement`、`test_lock_version_must_fit_declared_range`、`test_same_locked_version_cannot_have_different_revisions` | 已有锁文件匹配声明；同版本的不同 revision 不得伪装一致。 |
| `test_foundation_target_name_is_rejected` | 拒绝与系统框架同名的 Foundation target。 |
| `test_comments_do_not_create_fake_ui_imports` | 注释中的 import 示例不误判为真实 UI 依赖。 |
| `test_missing_native_tool_is_not_reported_as_pass` | 缺失原生检查工具时明确失败，不能跳过后报告通过。 |

生成物 `ios/Tests/test_ui_boundary.py` 覆盖 UI 产品链接、业务包/工程版本一致、App 根主题、iOS 平台依赖与页面材质；BUSINESS_MATERIAL_SOURCES 只放行登记的具体业务组件，不豁免平台或页面。原生导航、toolbar/alert 与菜单项不被禁止。同功能包装、登记理由、同 target 的 Feature 互引和生命周期仍需语义审查；静态检查不替代 Swift 编译、实际交互、OAuth 或购买验收。

## 平台编译回归

iOS `IOSControlTests` 另覆盖短暂原文与自定义图标、相同文本替换重启计时、紧凑 Toast 宽高、持续通知单行高度及辅助字号增长。示例 UI 回归 `testFeedbackToastAndCompactPersistentNotice` 验证明暗主题真实截图、短反馈自动消失、持续通知保留、同行操作的 44pt 触控范围及操作后关闭。

`.github/workflows/private-release.yml` 在 macOS 26 runner 执行完整 `swift test`，编译 `arm64-apple-macosx26.0`，并使用真实 iPhoneSimulator SDK 对列出的 iOS 目标执行 `swift build --target "$target" --triple arm64-apple-ios18.0-simulator --sdk "$ios_sdk_path" --scratch-path .build-ios`。iOS 目标清单不包含 Mac 展示 executable；交叉编译不代表目标设备交互通过。

## Mac 基础组件与 Playground

根 `swift test` 覆盖 `DesignKitMacTests` 与 `DesignKitMacPlaygroundTests`。前者验证主题/布局、公开字段壳与便利字段等价、原生 Combo 字号、可选焦点绑定、候选/标记文本与提交边界、Toast 原文/资源及生命周期，以及短提示自然收窄、相较旧通知卡减少高度、长文案在限定宽度换行增高；后者验证全部 22 个可视组件目录、双语资源、复制源码与 fixture 逐字一致、检索、两种宽度与状态宿主布局、公开独立和项目入口。

`MacFoundationComponentsTests` 检查浅色、深色及各自增加对比度的配色、文字与状态色对比度、标准字号和控件尺寸，以及应用强调色和悬停覆盖。另对照 AppKit 有效外观验证动态色解析，并渲染浅色、深色和自定义背景的共享卡片，检查实际像素。`MacControlHostTests` 用真实 AppKit Combo 验证应用的正文字号作用于原生编辑器，并核对 SwiftUI 字体映射。模板回归核对生成的 macOS 首页读取环境主题并由应用根注入 `.standard`。

修改示例后运行 `python3 apple/Sources/macOS/DesignKitMacPlayground/Scripts/sync-examples.py --check`。测试不连接设备、不写应用偏好；离屏宿主与回调测试不能替代真实 IME、VoiceOver、下拉鼠标和屏幕边缘验收。

## 邮箱密码组件

`apple/Tests/AuthCoreTests/TEST_CASES.md` 记录HTTP和会话回归，`apple/Tests/AuthUITests/TEST_CASES.md` 记录表单状态测试。示例工程的 `apple/Examples/EmailPasswordAuth/Tests/AuthFlowUITests.swift` 验证真实模拟器首次呈现、注册/重置导航、输入错误提示，不发送真实邮件。

## Mac 页面组合回收

`MacPlatformHostTests` 覆盖系统对话框按钮顺序、危险操作不绑定 Return、取消 Escape、动态提交可用性、模态取消返回原生第二按钮码、目录/文件类型限制、取消返回 nil、工具窗口关闭与生命周期策略、公开共享内容宿主，以及 Settings 窗口挂载后采用统一缩放和标题栏。另验证侧栏防折叠只影响所属分栏项。执行 `swift test --filter MacPlatformHostTests`，6 项测试不执行真实文件操作。

Playground 目录新增 page-header、settings-page、item-row、sidebar-item、application-icon、progress-panel-content、reorderable-list、management-list-style；每项保留中英说明和与编译 fixture 完全相同的可复制源码。现有目录完整性、资源同步与双宽度布局测试覆盖这些入口；原生桥接可用 `EPlatformHostPreview()` 人工操作。

`MacRecoveredCompositionTests` 覆盖共享标准布局别名与主题角色一致、原生排序插入位置与越界/多选边界、注入页边距影响真实宿主测量、长设置行自然增高、本机应用 Logo 与缺失应用符号，以及空态、自定义图标、表单、侧栏和进度面板组合的公开入口编译与布局。执行 `swift test --filter MacRecoveredCompositionTests`。

这些组件统一使用 `EControlTheme`；业务页保留权益、文件操作、排序持久化和导航回调。离屏宿主测试不代替真实拖拽、VoiceOver、键盘焦点及目标系统界面验收。

## iOS 原生弹框

公开组件为 `EAlert`、`EConfirm`、`EErrorAlert`，源码 `apple/Sources/iOS/DesignKit/EAlerts.swift`。独立宿主 `apple/Examples/IOSControls/IOSControlsApp.swift` 通过公开产品导入并挂载，`--dialogs-preview` 直接展示；用例位于 `apple/Examples/IOSControls/UITests/IOSControlsUITests.swift`。

| 用例 | 实际边界 |
|---|---|
| `testAlertDismissesAndCanReopenWithLocalizedText` | 中英文宿主资源在系统弹框显示，按钮关闭回写 false，关闭后可再次打开，保留真实截图 |
| `testConfirmCancelDoesNotPerformActionAndConfirmRunsOnce` | 呈现不执行回调；取消保留计数；危险确认每次增加一次，回写呈现绑定，关闭再开可继续确认 |
| `testErrorAlertPreservesRawMessageAndClearsBindingOnDismiss` | 初始 nil 不呈现；原文错误不做 key 查找；关闭清空绑定，相同错误可重新打开 |

按 `apple/Examples/IOSControls/README.md` 生成工程并运行 `IOSControlsUITests`；`swift test` 的 macOS 条件编译不能代表这些 iOS 弹框交互通过。测试不覆盖真实业务删除、异步请求成功、VoiceOver 朗读或多 scene 同时呈现。

## DesignCore 动效

`apple/Tests/DesignCoreTests/TEST_CASES.md` 记录 4 项动效测试，执行 `swift test --filter MotionTests`。覆盖系统减少动态效果时禁用动画、语义预设复用既有节奏、位移转场降为淡入和公开修饰符/旧按压 API 编译兼容。双平台完整交互示例位于 `apple/Examples/Motion`；纯策略测试不代替系统设置、指针和触控验收。
