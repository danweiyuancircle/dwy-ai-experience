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

已采用 DesignKitMac 的项目，通用控件、页面组合与平台 UI 优先使用基础库公开入口。通用颜色、字号、间距和圆角读取共享主题，不在产品维护第二套默认样式。系统版本适配留在基础组件内部；缺少必需能力时先补基础库、示例和验证，再迁移业务调用。原生 NSAlert、文件选择和工具窗口可以作为基础库内部实现；文件授权、危险操作、任务取消、权益和持久化仍属于业务。不要机械包装布局原语或把产品几何搬成全体默认值。具体能力以所选版本的 ios/Docs/Mac-Shared-Compositions.md 与 ios/Docs/Mac-Platform-Dialogs.md 为准。

查到对应版本源码后：同步查 `ios/Docs/SYNC_CORE.md` 与 `ios/Examples/OfflineSync/`；Apple 登录、Google 登录和邮箱密码分别查 `ios/Docs/APPLE_AUTH.md`、`ios/Docs/GOOGLE_AUTH.md`、`ios/Docs/EMAIL_PASSWORD_AUTH.md` 与相应示例。具体文件是否存在以所选 tag 为准。
