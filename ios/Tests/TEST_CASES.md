# 模板生成回归

从统一仓库根执行 `python3 -m unittest discover -s ios/Tests -p 'test_*.py'`。

| 用例 | 实际边界 |
| --- | --- |
| `test_ios_template_uses_versioned_components` | 执行 iOS 生成器，检查远端 URL、已发布 0.8.0-beta.4、E 组件与根主题、package 身份、目录重命名和旧来源/占位符缺席；执行生成物的 5 项 UI 边界检查，再注入 Mac import、页面玻璃和版本不一致，必须报告 3 项失败。 |
| `test_macos_template_uses_private_versioned_package` | 对 macOS 生成结果执行相同检查。 |
| `test_repository_root_override_locates_templates` | 显式传统一仓库根给 `--skeleton`，应找到 `ios/Templates`。 |

迁移时先在旧模板运行，因旧 URL 得到 2 failures，再更新生成器及模板，2 项通过。随后为仓库根覆盖参数增加回归，先得到 1 failure，再修复路径解析，最终 discover 3 项通过。额外实际运行两平台 `xcodegen generate` 和 `swift package dump-package`，确认可生成工程且 SwiftPM package 身份一致。

生成物 `Tests/test_ui_boundary.py` 覆盖 UI 产品链接、两份版本声明一致、App 根主题、iOS 不引入 Mac UI、页面不重做玻璃适配；原生导航、系统 toolbar/alert 与菜单项不被禁止。文本边界检查不替代 Swift 编译和实际交互。该回归不解析远端 tag，不执行宿主 OAuth 或真实购买。

## 平台编译回归

iOS `IOSControlTests` 另覆盖短暂原文与自定义图标、相同文本替换重启计时、紧凑 Toast 宽高、持续通知单行高度及辅助字号增长。示例 UI 回归 `testFeedbackToastAndCompactPersistentNotice` 验证明暗主题真实截图、短反馈自动消失、持续通知保留、同行操作的 44pt 触控范围及操作后关闭。

`.github/workflows/private-release.yml` 在 macOS 26 runner 执行完整 `swift test`，编译 `arm64-apple-macosx26.0`，并使用真实 iPhoneSimulator SDK 对列出的 iOS 目标执行 `swift build --target "$target" --triple arm64-apple-ios18.0-simulator --sdk "$ios_sdk_path" --scratch-path .build-ios`。iOS 目标清单不包含 Mac 展示 executable；交叉编译不代表目标设备交互通过。

## Mac 基础组件与 Playground

根 `swift test` 覆盖 `DesignKitMacTests` 与 `DesignKitMacPlaygroundTests`。前者验证主题/布局、公开字段壳与便利字段等价、原生 Combo 字号、可选焦点绑定、候选/标记文本与提交边界、Toast 原文/资源及生命周期，以及短提示自然收窄、相较旧通知卡减少高度、长文案在限定宽度换行增高；后者验证全部 22 个可视组件目录、双语资源、复制源码与 fixture 逐字一致、检索、两种宽度与状态宿主布局、公开独立和项目入口。

修改示例后运行 `python3 ios/Sources/macOS/DesignKitMacPlayground/Scripts/sync-examples.py --check`。测试不连接设备、不写应用偏好；离屏宿主与回调测试不能替代真实 IME、VoiceOver、下拉鼠标和屏幕边缘验收。

## 邮箱密码组件

`ios/Tests/AuthCoreTests/TEST_CASES.md` 记录HTTP和会话回归，`ios/Tests/AuthUITests/TEST_CASES.md` 记录表单状态测试。示例工程的 `ios/Examples/EmailPasswordAuth/Tests/AuthFlowUITests.swift` 验证真实模拟器首次呈现、注册/重置导航、输入错误提示，不发送真实邮件。

## DesignCore 动效

`ios/Tests/DesignCoreTests/TEST_CASES.md` 记录 4 项动效测试，执行 `swift test --filter MotionTests`。覆盖系统减少动态效果时禁用动画、语义预设复用既有节奏、位移转场降为淡入和公开修饰符/旧按压 API 编译兼容。双平台完整交互示例位于 `ios/Examples/Motion`；纯策略测试不代替系统设置、指针和触控验收。
