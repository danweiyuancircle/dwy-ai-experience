# Changelog

Apple App Kit（统一私有仓库中的 Apple 产品）版本记录。
**已上线的 App 默认不升级。** 要不要 bump，只看本节：兼容性、破坏面、不升会少什么。不要靠读 diff。

当前远程：https://github.com/danweiyuancircle/dwy-ai-experience.git
发版 = 改本文件 + 打 **同号 git tag**（首个完整私有发布版本 `0.4.1`）。

## 版本规则（0.x）

| 升 | 含义 | 已上线 App |
|----|------|------------|
| **patch**（0.2.0 → 0.2.1） | 只修 bug / 加文档，旧调用必须还能编、行为兼容 | 可不升 |
| **minor**（0.2.0 → 0.3.0） | 允许破坏 API 或持久化键 | **不要跟**，除非你主动要新能力并改完 App |
| **major**（1.0.0） | 公开稳定面；之后才按 SemVer 1.x 的 major=破坏 | — |

`Package.swift` 写 `from: "0.2.0"` 在 0.x 里等于 `>=0.2.0 <0.3.0`。`Package.resolved` 钉死具体 revision。
禁止 `path:` 本地源码，禁止 `branch: main`。

每一节必须有 **兼容性** 四行，缺一行不准打 tag。

---

## [0.4.1] - 2026-10-21

新项目模板切至统一私有仓库 `from: 0.4.1`。迁入通用 Apple 产品、AuthCore 与 iOS Google 适配器；Google SDK 统一到现有消费者使用的 9.1.0。私有 Release 同步提供 EAPI/auth Python 和 Web 包及 SHA256 清单。

`0.4.0` 源码标签保留；其首轮产物发布因 uv 自动生成的目录标记被严格清单拒绝，未形成完整 Release。`0.4.1` 清除该构建辅助文件后再校验，不放宽产物白名单。

### 兼容性

| 项 | 结论 |
|----|------|
| 相对 0.3.0 能否不改 App 继续编 | 既有产品/API 未删除或改名；新增认证产品为可选依赖，现有应用无需修改调用。 |
| 不升会怎样 | 没有共享 Google 授权、应用后端会话与 Keychain 刷新凭据能力。 |
| 升上来可选/必改项 | 接入认证时，宿主显式提供应用后端 URL、独立 namespace、Google iOS/web client ID 和回调 URL scheme；未接入认证的应用无需改配置。 |
| 最低系统 | 仍 iOS 17.0 / macOS 14.0 / Swift 6.0；Google 授权 UI 适配仅 iOS，纯 AuthCore 支持两端。 |

### Changed

- 根 `Package.swift` 统一保留十个产品名；通用源码迁至 `apple/Sources`，认证源码迁至 `modules/auth/apple/Sources`。
- 生成器与模板统一使用新私有仓库的版本引用，不把本机来源路径写进生成工程。历史版本链接保留作为原始发布记录。

### Added

- **AuthCore**：eapi HTTP 会话交换、刷新轮换、Keychain 凭据隔离、状态恢复、退出及在途响应撤销。
- **AuthGoogleIOS**：官方 Google SDK ID token 提供方。仅 Google 登录，不含邮箱密码或 Firebase。
- 接入说明见 `Docs/GOOGLE_AUTH.md`；ADBox、RightFlow 等业务客户端本轮均未接入。

---

## [0.3.0] - 2026-09-02

tag：`0.3.0`

新模块 + `LanguagePickerView` / `ThemePickerView` 从整页变成一行下拉。已钉 `from: "0.2.0"` 的 App **不会**自动拿到（0.x 的 `from: 0.2.0` = `>=0.2.0 <0.3.0`）。

### 兼容性

| 项 | 结论 |
|----|------|
| 相对 0.2.0 能否不改 App 继续编 | **能**。不升就还停在 0.2.x。升上来：没用过 kit 整页选择器的 App 不用改调用；用过的会变成一行，不要再 `NavigationLink`。 |
| 不升会怎样 | 没有 `PurchaseCore`；`LanguagePickerView` 仍是整页 List；模板仍是 0.2.0 依赖。 |
| 升上来建议改的 | 设置页嵌 `LanguagePickerView` / `ThemePickerView`；有付费改用 `LifetimeStore`，DEBUG 开关键 `debug.unlockAll`。 |
| 最低系统 | 仍 iOS 17.0 / macOS 14.0 / Swift 6.0 |

### Added

- **PurchaseCore**：`LifetimeStore`（StoreKit 2 终身买断）+ `StoreError` + `PurchaseAccess`。DEBUG 解锁键 `debug.unlockAll`，Release 无此字段。试用 / 次数限额不进 kit。
- **模板**：设置页解锁入口、极简付费墙、`App/Products.storekit`、`AppConfig.unlockProductID`。
- **模板设置「关于」**：版本号、隐私政策、意见反馈（`mailto:` 拉起系统邮箱）、给个好评（`requestReview` 系统评价框）。第 3 次进入根页再请评一次。kit 不动。

### Changed

- **DesignCore**：`LanguagePickerView` / `ThemePickerView` 改为本页 `Picker(.menu)` 一行，不再是整页 List。
- 模板 `Package.swift` / `project.yml`：`from: "0.3.0"`。
- **macOS ThemeManager**：写 `NSWindow.appearance` 时跳过 `NSStatusBarWindow`。
- **L10nKit**：`loc()` 在主线程读取 `LocalizationManager.language`，SwiftUI `body` 切语言会当场重绘。

已钉 0.2.0 的菜单栏 App（Focus）须在产品侧自行隔离状态项窗，或升到含此修复的 tag。未升 kit 的 App 切语言要在各 `View.body` 读 `localization.language`。

---

## [0.2.0] - 2026-08-12

tag：`0.2.0` → `85fecbd`

### 兼容性

| 项 | 结论 |
|----|------|
| 相对 0.1.0 能否不改 App 继续编 | **能**。只加 API，没删符号、没改 UserDefaults 键。 |
| 不升会怎样 | macOS「浅色 → 跟随系统」可能卡住浅色；没有 `AppLog.flush` / 现成导出文件名。 |
| 升上来建议改的（可选） | 根视图 `.preferredColorScheme(theme.mode.colorScheme)` 改成 `theme.preferredColorScheme`，才能吃到跟随系统修复。不改也能编。 |
| 最低系统 | 仍 iOS 17.0 / macOS 14.0 / Swift 6.0 |

**已钉 0.2.0 的上线包：停住即可。** 没有安全补丁。

### Added

- **LogKit**：`AppLog.flush(timeout:)`；`LogExport.makeFileName(prefix:date:)`。
- **DesignKitIOS**：`ThemeManager.preferredColorScheme`（与 macOS 对齐）。
- **DesignKitMac**：`preferredColorScheme`、`systemAppearanceRevision`、系统外观通知、`configureDefault(_:)`。
- **模板**：设置页「导出日志」；启动时显式轮转（2MB × 5 归档）；文案 key `settings_export_logs*`、`common_ok`。

### Changed

- **LogExport.exportZip**：导出前自动 flush。
- **macOS ThemeManager**：同步/清空各 `NSWindow.appearance`，避免窗口粘住旧方案。
- **模板根视图**：改用 `theme.preferredColorScheme`。

### Fixed

- **macOS 跟随系统**：先选浅色再选「跟随」，系统为深色时窗口不再停在浅色。
  根因：system 档对 SwiftUI 传 `nil` 不重置。现解析成当前系统黑/白。

---

## [0.1.0] - 2026-08-10

提交：`1c896fb`（**当时没打 git tag**；历史起点，不要再往这钉新 App）。

### 兼容性

| 项 | 结论 |
|----|------|
| 新 App | 不要用。从 0.2.0 起。 |
| 若有人还停在这份源码 | 缺跟随系统修复、缺 flush/导出文件名；API 面是初版。 |
| 最低系统 | iOS 17.0 / macOS 14.0 / Swift 6.0 |

### Added

- **CoreKit**：`AppError`、`ByteCount`、`Hex`、`TimeFormat`
- **LogKit**：`AppLog`、`LogConfig`、`AppLogger`、Puppy 轮转、`LogExport.exportZip`
- **L10nKit**：`LocalizationManager`、`AppLanguage`、`loc()`；可用 `configure(supported:)` 收窄语言
- **CacheKit**：`DiskCache`
- **DesignCore**：`ThemeMode`、`Motion`、语言/主题选择页
- **DesignKitIOS / DesignKitMac**：各端 `ThemeManager`
- 四层模板 + `scripts/new-app.sh`

当时业务仓按 **path 依赖** 用这份源码；0.2.0 起改为 git tag。

---

## 一览（倒序，给「要不要升」扫一眼）

| 版本 | 日期 | 破坏？ | 不升会少什么 | 已上线建议 |
|------|------|--------|--------------|------------|
| **0.3.0** | 2026-09-02 | LanguagePicker 变行；新 PurchaseCore | 无买断骨架、选择器仍是整页 | 要买断/下拉再 bump；其余钉 0.2.0 |
| **0.2.0** | 2026-08-12 | 无 | 跟随系统修复、日志 flush | **钉住** |
| 0.1.0 | 2026-08-10 | — | 初版 | 不要新钉 |

[0.3.0]: https://github.com/danweiyuancircle/apple-app-kit/releases/tag/0.3.0
[0.2.0]: https://github.com/danweiyuancircle/apple-app-kit/releases/tag/0.2.0
