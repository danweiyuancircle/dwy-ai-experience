---
name: dwy-apple-appkit
description: 使用或排查 AppleAppKit SwiftPM 自有基础库时使用，按模块和项目锁定版本查证接口。
---

# AppleAppKit 自有基础库

先查项目 Package.resolved、实际 checkout 和已使用的产品；版本范围不是锁定版本。源码及示例只在与项目锁定版本一致时作为依据。

- SyncCore：同步；CoreKit、LogKit、L10nKit、CacheKit：基础功能、日志、本地化与缓存。
- DesignCore、DesignKitIOS、DesignKitMac：跨平台及平台界面能力。
- AuthCore、AuthUI、AuthGoogleIOS、AuthAppleIOS、AuthGoogleMac：认证核心与平台接入。
- PurchaseCore：购买能力。

团队新 iOS 项目通过 `DesignKitIOS` 统一消费 UI 基础件；默认模板入口为 `ios/scripts/new-app.sh --platform ios`。控件主题在 App/独立 scene 根装配，系统版本和通用材质差异留组件内部；项目只组合品牌与业务，不复制已有 E 组件。原生导航、菜单项、toolbar/alert 与认证品牌控件按平台契约保留。具体边界见 `dwy-ios-development/references/design-system.md`，产品使用与示例查对应版本的 `ios/Docs/UI_FOUNDATION_IMPLEMENTATION.md`、`ios/Examples/IOSControls/`。

按目标平台查 Package.swift、对应公开声明和 ios/README.md，再核对初始化、生命周期、系统版本与错误处理。找不到确切版本时查对应语义化 Git tag；不可用时说明缺口，不以默认分支替代。使用新产品或新增依赖遵守项目选择和授权，不擅自安装。

查到对应版本源码后：同步查 `ios/Docs/SYNC_CORE.md` 与 `ios/Examples/OfflineSync/`；Apple 登录、Google 登录和邮箱密码分别查 `ios/Docs/APPLE_AUTH.md`、`ios/Docs/GOOGLE_AUTH.md`、`ios/Docs/EMAIL_PASSWORD_AUTH.md` 与相应示例。具体文件是否存在以所选 tag 为准。
