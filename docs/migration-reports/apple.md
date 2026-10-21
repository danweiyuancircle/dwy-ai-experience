# Apple 框架与客户端认证迁移报告

状态：迁移完成，目标仓库验证通过；未提交、未打 tag、未发布。验证时间：2026-10-21（Asia/Taipei）。

## 来源与完整性

来源为旧 Apple 框架 `$SOURCE_ROOT`（原 ios-arc）当前工作树，包括未提交的 manifest/lock/CHANGELOG，以及未跟踪的 AuthCore、AuthGoogleIOS、AuthCoreTests、GOOGLE_AUTH 文档。共迁入 89 个来源文件。

逐文件来源路径、目标路径、来源与目标 SHA256、变化标识、来源 HEAD/dirty status，见 `docs/migration-reports/apple-sources.json`。迁移结束重验：来源文件哈希、HEAD、dirty status 均未变化；所有运行时 Swift 源码逐字节一致；原有测试完整保留；锁文件与十项第三方 pin 保持一致。未复制来源 `.git`、`.build`、`.swiftpm` 或缓存。

## 物理归属

| 内容 | 目标 |
| --- | --- |
| SwiftPM manifest/lock | `Package.swift`、`Package.resolved` |
| 通用框架 | `apple/Sources` |
| 通用框架原有测试 | `apple/Tests` |
| AuthCore / AuthGoogleIOS | `modules/auth/apple/Sources/AuthCore`、`modules/auth/apple/Sources/AuthGoogleIOS` |
| AuthCore 原有测试 | `modules/auth/apple/Tests/AuthCoreTests` |
| 模板、生成器、文档 | `apple/Templates`、`apple/scripts`、`apple/Docs` |

根 manifest 的 10 个 product 名保持不变：CoreKit、LogKit、L10nKit、CacheKit、DesignCore、DesignKitIOS、DesignKitMac、PurchaseCore、AuthCore、AuthGoogleIOS；16 个 target 的实际目录均存在。最低系统保持 iOS 17 / macOS 14。认证仍为 Google-only，iOS 呈现层与双平台纯认证核心独立，无新依赖、无业务 App UI 接入。

## 模板变更与 TDD

生成器 `apple/scripts/new-app.sh` 将新项目绑定到 `https://github.com/danweiyuancircle/dwy-ai-experience.git`，`from: 0.4.0`，SwiftPM package identity 为 `dwy-ai-experience`。保留版本依赖；不写本机来源路径或凭据。

先增加 `apple/Tests/test_templates.py`，在原模板实际执行后得到 2 failures，原因均为旧远程 URL；再更新生成器、SwiftPM/XcodeGen 模板和来源文档，2 项通过。随后增加 `--skeleton` 显式传仓库根的兼容回归，先得到 1 failure，再修正模板资源路径为 `apple/Templates`，最终 3 项通过。生成结果检查版本、package 身份、文件/目录重命名、旧来源缺席、占位符完全替换。历史 CHANGELOG 的旧 tag 链接保留为原发布记录。

## 实际验证

环境：Xcode 27.1（27A9275）、Apple Swift 6.4。默认系统 developer directory 为 CLT，所有 Swift 命令均局部设置 `DEVELOPER_DIR`，未改全局选择。

先将 `DEVELOPER_DIR` 指向已安装 Xcode 的 Developer 目录，并设置 `IOS_SIMULATOR_SDK="$(xcrun --sdk iphonesimulator --show-sdk-path)"`。从仓库根目录执行：

```bash
swift test
python3 -m unittest discover -s apple/Tests -p 'test_*.py'
swift build \
  --target AuthGoogleIOS \
  --triple arm64-apple-ios17.0-simulator \
  --sdk "$IOS_SIMULATOR_SDK" \
  --scratch-path .build-ios --cache-path .build --skip-update
```

| 检查 | 实际结果 |
| --- | --- |
| 完整 macOS `swift test` | exit 0；43 项、0 failures |
| AuthCoreTests | 18 项：HTTP 5、会话状态机 10、Keychain 3 |
| 其余 XCTest | CoreKit 3、LogKit 9、L10nKit 4、CacheKit 3、PurchaseCore 6 |
| iPhone Simulator AuthGoogleIOS | exit 0；811 个构建步骤，6.51 秒；官方 Google SDK 与传递依赖参与真实 iOS 编译 |
| 模板 unittest discover | exit 0；3 项、0 failures |
| 两平台 `xcodegen generate` | 均生成实际 Xcode 工程，新 URL 与 minimumVersion 0.4.0 进入 pbxproj |
| 两平台 `swift package dump-package` | 均解析 manifest，identity 为 dwy-ai-experience |
| 根 manifest 形状 | 10 products / 16 targets，目录全部存在 |
| 来源与依赖核对 | 89 来源文件/HEAD/dirty status 未变化；运行时 Swift 源码字节一致；所有 pin 一致 |

iOS 实际模块：`.build-ios/out/Products/Debug-iphonesimulator/AuthGoogleIOS.swiftmodule/arm64-apple-ios-simulator.swiftmodule`；实际 provider object 为 `.build-ios/out/Intermediates.noindex/AppleAppKit.build/Debug-iphonesimulator/AuthGoogleIOS-t.build/Objects-normal/arm64/GoogleSignInProvider.o`。

机器可读结果为 `apple/validation/results.json`。原始红绿、模板工程、最终 Swift test、iOS build 日志均保留于本地 `apple/validation`，由 `apple/validation/.gitignore` 排除；提交内容仅保留紧凑 `apple/validation/results.json` 与路径说明 `apple/validation/README.md`。

## 环境问题与验收边界

第一次全历史 GoogleSignIn 获取超时，后续官方浅取出现 `curl 18` / early EOF；最终在目标 `.build` 使用单命令 HTTP/1.1，从官方 tag 9.0.0 抓取，revision 与原锁定值 `3996d908c7b3ce8a87d39c808f9a6b2a08fbe043` 一致。未改全局 Git 设置。

系统 SwiftPM AppAuth 缓存为 `blob:none` 部分克隆，共享 checkout 缺 blob。仅把目标中的失败缓存移到目标 `.build` 备份，再从官方 tag 2.1.0 建全新浅取，revision 与原锁定值 `a7caeda164dc5108bf4649472b28a5af65dc6f33` 一致。修复后以目标实际源码完整重编译、重跑；未用原工程测试冒充。iOS 使用独立 scratch directory，仅复用目标刚解析的第三方依赖缓存。

保留已知警告：GoogleUtilities 为锁住 8.1.4 而显式声明，根 target 未直接使用其 product；iOS 验证的 `--skip-update` 有 deprecated 提示。最终裸 `swift test` 无 `--skip-update`。

0.4.0 只是下一次 SwiftPM 发布版本，本任务未创建 tag；生成项目在该 tag 发布前不能完成远端版本解析。本次模板验证仅证明生成器、manifest、Xcode 工程结构正确。未宣称真实 Google OAuth、宿主 UI 接入、后端部署或生产验收；仍须在真实配置下验证登录/取消/恢复/刷新轮换/退出/断网/换账号。业务 App 工程与原目录均未修改。

## 验收前清理

仅去除迁入 Markdown 的行尾空白，文档与清单改用从仓库根起的完整相对路径或 `$SOURCE_ROOT` 等可移植占位符；来源真实路径只保留在本地 `.superpowers` 实现报告。运行时 Swift 源码仍与来源逐字节一致，来源未修改。原始验证日志与再生 manifest 结构输出保留本地，不进入版本树。
