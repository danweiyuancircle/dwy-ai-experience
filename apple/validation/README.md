# Apple 迁移验证证据

可提交结果：`apple/validation/results.json`。迁移说明与来源哈希清单位于 `docs/migration-reports/apple.md`、`docs/migration-reports/apple-sources.json`。

原始证据仅保留本地，不进入版本树：

| 内容 | 从仓库根起的本地路径 |
| --- | --- |
| 最终完整 macOS 测试 | `apple/validation/swift-test-final.log` |
| 真 iPhone Simulator 编译 | `apple/validation/ios-build.log` |
| 模板最终 discover | `apple/validation/template-discover.log` |
| URL 迁移红测、根目录参数红测 | `apple/validation/template-red.log`、`apple/validation/template-root-red.log` |
| 两平台 Xcode 工程与 manifest 检查 | `apple/validation/template-projects.log` |
| 下载、缓存诊断及先前失败 | `apple/validation/*fetch*.log`、`apple/validation/swift-test-*interrupted.log` 等 |
| 可再生的 manifest 结构快照 | `apple/validation/package-shape.json` |

临时生成的模板工程创建于系统临时目录，验证后已删除。编译产物位于已忽略的 `.build` 与 `.build-ios`，Python 缓存由 `apple/.gitignore` 排除。

在已选择完整 Xcode 的环境中，从仓库根运行：

```bash
swift test
python3 -m unittest discover -s apple/Tests -p 'test_*.py'
IOS_SIMULATOR_SDK="$(xcrun --sdk iphonesimulator --show-sdk-path)"
swift build --target AuthGoogleIOS --triple arm64-apple-ios17.0-simulator \
  --sdk "$IOS_SIMULATOR_SDK" --scratch-path .build-ios
```

`DEVELOPER_DIR` 可按本机 Xcode 安装位置指定。来源核对时将 `$SOURCE_ROOT` 解析为本机旧 Apple 框架目录；该目录不写入可提交清单。
