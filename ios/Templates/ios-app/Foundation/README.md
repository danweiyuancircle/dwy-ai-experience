# ④ Foundation（业务无关基础层）

对应 TVRemote 的 `Sources/Foundation/*`。

本目录是**层锚点**，保证工程树一眼能看到四层。
**实现在 AppleAppKit git tag**，业务仓不要复制一套 Log/L10n 源码。

## 本工程使用的 product（骨架）

| Product | 职责 |
|---------|------|
| CoreKit | AppError、工具 |
| LogKit | AppLog 本地日志（按大小轮转）+ LogExport 导出 |
| L10nKit | loc / 多语言 |
| CacheKit | DiskCache |
| DesignCore | ThemeMode、Motion、语言/外观**本页下拉** |
| DesignKitIOS | iOS ThemeManager |
| PurchaseCore | 终身买断 `LifetimeStore` + DEBUG 解锁 |

依赖见根目录 `Package.swift` / `project.yml`：`dwy-ai-experience` git tag，禁止 path。

## 改 ④ 层代码

在骨架仓改并打 tag → 各 App 自己决定是否 bump。
仅本 App 需要的逻辑 → 进 `BizFoundation/`，不要塞进骨架。
