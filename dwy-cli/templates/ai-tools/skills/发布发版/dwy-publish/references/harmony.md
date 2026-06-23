# 鸿蒙发布流程

适用：HarmonyOS ArkTS 产物——**应用包（har app / hap）** 或 **SDK（har→ohpm）**。

## 版本（通用步，固化）

- `oh-package.json5` 的 `version` = 语义版本号，走 `../dwy-semver` 决策 + bump.py。
- 多文件同步见 `version-sync.md`。

## build / publish（项目步，不写死命令）

命令来自缓存（build_cmd/publish_cmd），缓存缺则按 `publish-config.md` 探测：
- 探测线索：`build-profile.json5`、ohpm 脚本、DevEco 构建配置、CI workflow
- 探测不到→问用户→缓存

按缓存 method 分流：
- `ohpm` → 用项目实际的 ohpm 发布命令（中心仓 / 私有源）
- `github-action` → 引 `../dwy-github-action-publish`（先过通用检查）
- `local` → 缓存的本地构建/发布命令

## changelog / 安全检查 / 监控

- changelog → `changelog.md`（写 `harmony/CHANGELOG.md`）
- 安全检查 → `../dwy-sdk-spec`
- 监控 + 结果 → `monitor-notify.md`
