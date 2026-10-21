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

`.github/workflows/private-release.yml` 执行完整 `swift test`，并使用真实 iPhoneSimulator SDK 对全部产品执行 `swift build --triple arm64-apple-ios17.0-simulator --sdk "$ios_sdk_path" --scratch-path .build-ios`。全产品构建覆盖 macOS 主题监听的平台隔离，避免只编译 AuthGoogleIOS 时漏掉 `DistributedNotificationCenter` 的 iOS 编译错误。

## 邮箱密码组件

`ios/Tests/AuthCoreTests/TEST_CASES.md` 记录HTTP和会话回归，`ios/Tests/AuthUITests/TEST_CASES.md` 记录表单状态测试。示例工程的 `ios/Examples/EmailPasswordAuth/Tests/AuthFlowUITests.swift` 验证真实模拟器首次呈现、注册/重置导航、输入错误提示，不发送真实邮件。
