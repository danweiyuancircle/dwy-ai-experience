# iOS 发布流程

适用：iOS 产物——**应用包（ipa→TestFlight/App Store）** 或 **SDK（framework/xcframework→CocoaPods/SPM）**。

## 先判产物形态

- 应用包：有 app target、`fastlane/` beta/release lane、TestFlight 上传 → 走 app 路径
- SDK：产出 framework/xcframework、有 podspec / `Package.swift` → 走 SDK 路径

## 版本（通用步，固化）

- 语义版本号 `CFBundleShortVersionString`，走 `../dwy-semver` 决策 + bump.py。
- **build 号 `CFBundleVersion` = 时间戳 `yyyyMMddHHmm` 12 位**（如 `202606231430`，`date +%Y%m%d%H%M`），每次发布重新生成，单调递增。app 和 SDK 都适用。
- 多文件同步见 `version-sync.md`。

## build / publish（项目步，不写死命令）

命令来自缓存（`release_config.sh` 的 build_cmd/publish_cmd），缓存缺则按 `publish-config.md` 探测：
- 探测线索：`fastlane/Fastfile`、`*.xcodeproj`/`*.xcworkspace`、`Makefile`、CI workflow、`package.json` scripts
- 探测不到→问用户→缓存

按缓存 method 分流：
- `testflight` → 用项目实际的 TestFlight 上传命令（fastlane lane / Transporter / altool）
- `cocoapods` / `spm` → 用项目实际的 pod 发布 / git tag 命令（SPM 以 tag 为版本，tag 须等于 `CFBundleShortVersionString`）
- `github-action` → 引 `../dwy-github-action-publish`（先过其通用检查）
- `local` → 缓存的本地命令

## changelog / 安全检查 / 监控

- changelog → `changelog.md`（写 `ios/CHANGELOG.md`）
- 安全检查 → `../dwy-sdk-spec`（SDK 发布尤其要查泄露）
- 监控 + 结果 → `monitor-notify.md`
