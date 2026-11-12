# 模板生成回归

从统一仓库根执行 `python3 -m unittest discover -s ios/Tests -p 'test_*.py'`。

| 用例 | 实际边界 |
| --- | --- |
| `test_ios_template_uses_private_versioned_package` | 执行 iOS 生成器，检查新 URL、0.4.1、package 身份、目录重命名和旧来源/占位符缺席。 |
| `test_macos_template_uses_private_versioned_package` | 对 macOS 生成结果执行相同检查。 |
| `test_repository_root_override_locates_templates` | 显式传统一仓库根给 `--skeleton`，应找到 `ios/Templates`。 |

迁移时先在旧模板运行，因旧 URL 得到 2 failures，再更新生成器及模板，2 项通过。随后为仓库根覆盖参数增加回归，先得到 1 failure，再修复路径解析，最终 discover 3 项通过。额外实际运行两平台 `xcodegen generate` 和 `swift package dump-package`，确认可生成工程且 SwiftPM package 身份一致。

该回归不解析尚未发布的 0.4.1 远端 tag，不执行宿主 OAuth，也不新增业务 App UI。

## 平台编译回归

`.github/workflows/private-release.yml` 在 macOS 26 runner 执行完整 `swift test`，编译 `arm64-apple-macosx26.0`，并使用真实 iPhoneSimulator SDK 对列出的 iOS 目标执行 `swift build --target "$target" --triple arm64-apple-ios18.0-simulator --sdk "$ios_sdk_path" --scratch-path .build-ios`。iOS 目标清单不包含 Mac 展示 executable；交叉编译不代表目标设备交互通过。

## Mac 基础组件与 Playground

根 `swift test` 覆盖 `DesignKitMacTests` 与 `DesignKitMacPlaygroundTests`。前者验证主题/布局、公开字段壳与便利字段等价、原生 Combo 字号、可选焦点绑定、候选/标记文本与提交边界、Toast 原文/资源及生命周期，以及短提示自然收窄、相较旧通知卡减少高度、长文案在限定宽度换行增高；后者验证全部 22 个可视组件目录、双语资源、复制源码与 fixture 逐字一致、检索、两种宽度与状态宿主布局、公开独立和项目入口。

修改示例后运行 `python3 ios/Sources/macOS/DesignKitMacPlayground/Scripts/sync-examples.py --check`。测试不连接设备、不写应用偏好；离屏宿主与回调测试不能替代真实 IME、VoiceOver、下拉鼠标和屏幕边缘验收。

## 邮箱密码组件

`ios/Tests/AuthCoreTests/TEST_CASES.md` 记录HTTP和会话回归，`ios/Tests/AuthUITests/TEST_CASES.md` 记录表单状态测试。示例工程的 `ios/Examples/EmailPasswordAuth/Tests/AuthFlowUITests.swift` 验证真实模拟器首次呈现、注册/重置导航、输入错误提示，不发送真实邮件。
