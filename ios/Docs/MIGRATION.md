# iOS/macOS 框架维护入口

AppleAppKit 已合入开发套件仓库 `dwy-shared`，统一 Git 来源为 `https://github.com/danweiyuancircle/dwy-ai-experience.git`。后续修改在本仓 `ios/` 内进行，不再维护独立 `ios-arc` 工作树。

## 当前目录

- `ios/Sources/Shared/`：跨平台基础能力与 AuthCore。
- `ios/Sources/iOS/`：iOS UI 基建与 AuthGoogleIOS。
- `ios/Sources/macOS/`：macOS UI 基建。
- `ios/Tests/`：框架、认证与模板生成测试。
- `ios/Templates/`、`ios/scripts/`、`ios/Docs/`：模板、生成器和接入文档。

仓库根 `Package.swift` / `Package.resolved` 保留为远程 SwiftPM 的必要入口和依赖锁文件，所有 target 指向 `ios/`。十个 product 名、公开 API、iOS 17 / macOS 14 部署底线保持不变。

## 历史版本

`0.4.1` 标签与私有 Release 保持原内容；当前目录整理尚未发布新版本。业务应用继续使用原有固定版本，后续升级由各应用单独决定。

来源清单和初次迁移哈希保存在 `docs/migration-reports/apple-sources.json`，历史验证记录见 `docs/migration-reports/apple.md`。其中 `apple/`、`modules/auth/apple/` 均为初次迁移的历史路径。

旧目录中的未提交认证源码与测试已承接到本仓；Google SDK 适配器保留统一仓库现有的 9.1.0 和 Swift 并发兼容实现。应用账户、业务数据库和登录配置仍由各宿主独立维护。

## 复现验证

从统一仓库根运行：

```bash
swift package dump-package
python3 -m unittest discover -s ios/Tests -p 'test_*.py'
swift test --force-resolved-versions
ios_sdk_path="$(xcrun --sdk iphonesimulator --show-sdk-path)"
swift build --force-resolved-versions --triple arm64-apple-ios17.0-simulator --sdk "$ios_sdk_path"
```

框架单测和 SDK 编译不包含业务应用接入及真实 Google OAuth 验收。

## 本次本地验证（2026-10-21）

| 检查 | 结果 |
| --- | --- |
| 原统一仓库文件迁移 | 92 个文件均在新位置，未遗漏；另承接旧框架迁移说明。 |
| SwiftPM 包清单 | 10 个 product、16 个 target，所有 target 路径均位于 `ios/`。 |
| 完整 Swift 单测 | 43 项通过、0 失败，其中 AuthCoreTests 18 项。 |
| 真实模板生成 | iOS、macOS、仓库根覆盖参数共 3 项通过。 |
| iOS 全产品编译 | 使用真实 iPhoneSimulator SDK 与 `arm64-apple-ios17.0-simulator`，exit 0。 |
| 依赖锁定 | `Package.resolved` 未改动；复验使用 `--force-resolved-versions`。 |
| 旧目录依赖 | RightFlow、Quadrant、ADBox 的包配置没有指向旧目录的本地依赖；新构建缓存不借用旧目录对象。 |

全产品模拟器编译发现并修复 macOS 主题监听缺少平台判断的问题；`.github/workflows/private-release.yml` 现持续编译全部产品，覆盖该回归。

初次网络拉取超时后，复验以 `--skip-update` 使用本地完整 Git 缓存；缓存中的锁定源码已独立复制，未修改依赖版本。本节为本地验证结果，不代表远端 CI 或新版本发布。
