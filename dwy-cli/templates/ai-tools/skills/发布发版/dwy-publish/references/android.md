# Android 发布流程

适用：Android 产物——**应用包（apk/aab→分发/商店）** 或 **SDK（aar→maven）**。

## 先判产物形态

- 应用包：有 application module、产出 apk/aab → 走 app 路径
- SDK：library module、产出 aar、有 maven publish 配置 → 走 SDK 路径

## 版本（通用步，固化）

- `versionName` = 语义版本号，走 `../dwy-semver` 决策 + bump.py。
- `versionCode` = 单调递增整数，每次发布 +1。
- 多文件同步见 `version-sync.md`。

## build / publish（项目步，不写死命令）

命令来自缓存（build_cmd/publish_cmd），缓存缺则按 `publish-config.md` 探测：
- 探测线索：`build.gradle(.kts)` task、`gradlew`、`fastlane/`、CI workflow
- 探测不到→问用户→缓存

按缓存 method 分流：
- `maven` → 用项目实际的 maven 发布命令（gradle publish task / 私有源）
- `github-action` → 引 `../dwy-github-action-publish`（先过通用检查）
- `local` → 缓存的本地构建/发布命令

## changelog / 安全检查 / 监控

- changelog → `changelog.md`（写 `android/CHANGELOG.md`）
- 安全检查 → `../dwy-sdk-spec`
- 监控 + 结果 → `monitor-notify.md`
