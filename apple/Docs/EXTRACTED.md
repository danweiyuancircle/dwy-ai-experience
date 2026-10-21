# 抽取对照

源项目：

- iOS：`$TV_REMOTE_SOURCE_ROOT`
- macOS：`$FOCUS_SOURCE_ROOT`（Focus）

| 骨架模块 | 主要来源 | 调整 |
|----------|----------|------|
| CoreKit / AppError | 两边相同 | 合并 |
| CoreKit / ByteCount、Hex | TVRemote | 保留 |
| CoreKit / TimeFormat | Focus | 保留 |
| LogKit / AppLog 门面 | Focus（更干净） | subsystem/fileName 由 App 注入 |
| LogKit / LogExport | TVRemote | 目录优先 `AppLog.directoryURL` |
| L10nKit | 两边 + TV 多语枚举 | `configure(supported:)` 收窄列表 |
| DesignCore / ThemeMode、Motion | Focus | 共享层 |
| DesignCore / LanguagePicker、ThemePicker | 新建（范式来自两边设置页） | **本页下拉**，不是整页 List |
| PurchaseCore / LifetimeStore | EasyJPG / EasyFit / EasyZip / TVRemote | 终身买断 + DEBUG 解锁；试用 / 限额留 App |
| DesignKitIOS / ThemeManager | TVRemote | 独立 iOS 树 |
| DesignKitMac / ThemeManager | Focus | 独立 macOS 树 |
| CacheKit / DiskCache | TVRemote | 原样迁入 |

**有意未进骨架（业务或平台过重）**

- 试用天数 / 免费次数门控（产品规则，不进 PurchaseCore）
- 品牌 Palette 色值
- ADB / 番茄钟 / MenuBar 业务
- Haptics、ShareSheet、SwipeBack（可二期放 PlatformKit）
