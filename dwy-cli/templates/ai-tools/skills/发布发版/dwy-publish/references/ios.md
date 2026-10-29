# iOS 发布流程

适用：iOS 产物——**应用包（ipa→TestFlight/App Store）** 或 **SDK（framework/xcframework→CocoaPods/SPM）**。

## 先判产物形态

- 应用包：有 app target、`fastlane/` beta/release lane、TestFlight 上传 → 走 app 路径
- SDK：产出 framework/xcframework、有 podspec / `Package.swift` → 走 SDK 路径

## 版本（通用步，固化）

- 语义版本号 `CFBundleShortVersionString`，走 `../dwy-semver` 决策 + bump.py。
- 构建号 `CFBundleVersion` 遵循项目及发布渠道约定；重新上传构建时满足渠道的递增要求。
- 多文件同步见 `version-sync.md`。

## build / publish（项目步，不写死命令）

命令来自缓存（`release_config.sh` 的 build_cmd/publish_cmd），缓存缺则按 `publish-config.md` 探测：
- 探测线索：`fastlane/Fastfile`、`*.xcodeproj`/`*.xcworkspace`、`Makefile`、CI workflow、`package.json` scripts
- 探测不到→问用户→缓存

按缓存 method 分流：
- `testflight` → 用项目实际的 TestFlight 上传命令（fastlane lane / Transporter / altool）
- `cocoapods` / `spm` → 用项目实际的 pod 发布命令（SPM 消费 git tag；tag 走统一 `git-tag.md`，版本串 = changelog = `CFBundleShortVersionString`）
- `github-action` → 引 `../dwy-github-action-publish`（先过其通用检查）
- `local` → 缓存的本地命令

## changelog / tag / 安全检查 / 监控

- changelog → `changelog.md`（使用该工程既有路径和格式）
- tag → `git-tag.md`（每次 bump 必打；版本串与 changelog 标题一致）
- 安全检查 → `../dwy-sdk-spec`（SDK 发布尤其要查泄露）
- 监控 + 结果 → `monitor-notify.md`
