---
name: dwy-apple-appkit
description: 使用或排查 AppleAppKit SwiftPM 自有基础库时使用，按模块和项目锁定版本查证接口。
---

# AppleAppKit 自有基础库

## 维护 AppleAppKit 版本时

仅在维护 AppleAppKit 源码仓库时适用：更新版本、Changelog 或创建/发布语义化 tag 前，对照上一发布 tag 检查本 Skill 与平台引用资料是否仍准确，覆盖公开产品/API、初始化/生命周期、权限配置、最低系统/工具链、废弃迁移及示例路径。需要同步的内容必须进入新 tag；无需更新时在该版本 Changelog 中记录“Skill 同步检查：无需更新”及具体依据。该检查不授权更新消费者依赖、推送/发布或修改全局 Skills。

## 在应用项目中使用

项目内部仍为 App①、Features②、BizFoundation③、Foundation④四层，产品 BusinessUI 属于②，平台业务适配属于③；AppleAppKit 的通用产品对应④。单端、双端的统一目录与生成入口见 `dwy-apple-architecture`，不因增加包而增加层级，也不在消费项目建立空 Foundation 层锚点。

权限能力先检查所选 tag 是否包含 `PermissionCore`、`PermissionIOS`、按需 `Permission*IOS`、`PermissionMac` 与 `PermissionUI`，再查该 tag 的 `apple/Docs/Permissions.md`。普通互联网、本地网络、所选文件和完整磁盘访问的机制不同，不套用统一授权 Bool；limited、restricted、provisional 和 unknown 必须保留。用途声明、entitlements、签名和业务恢复归宿主；设置跳转成功不代表授权成功。权限 UI 按需链接，不把全部权限框架默认引入应用。

先查项目 Package.resolved、实际 checkout 和已使用的产品；版本范围不是锁定版本。源码及示例只在与项目锁定版本一致时作为依据。

- SyncCore：同步；CoreKit、LogKit、L10nKit、CacheKit：基础功能、日志、本地化与缓存。
- DesignCore、DesignKitIOS、DesignKitMac：跨平台及平台界面能力。
- DesignKitMac 0.10.0 起提供 `ePreventsSidebarCollapse`，用于 SwiftUI 原生分栏的侧栏内容。
- `eWindowOverlay` 仅存在于 0.10.0 / 0.10.1，0.11.0 已移除。模态弹框改用 SwiftUI `.sheet` / `.alert` / `.confirmationDialog` 或 AppKit sheet；确认与错误提示用 `EAlert`、`eErrorAlert`，文件选择用 `EFileDialog`。迁移时删除宿主为页内弹框补的菜单禁用和事件监听阻断，按 sheet 重新验收键盘与焦点。
- AuthCore、AuthUI、AuthGoogleIOS、AuthAppleIOS、AuthGoogleMac：认证核心与平台接入。
- PurchaseCore：购买能力。
- PermissionCore、PermissionIOS、按需 Permission*IOS、PermissionMac、PermissionUI：从 0.9.0 起提供权限状态、申请、设置引导与可选说明 UI；旧标签不具备这些产品。

从 0.9.0 起，DesignKitIOS 的 EAlert、EConfirm、EErrorAlert 是公开 ViewModifier，通过 .modifier(EAlert(...)) 等方式挂载到当前 scene 的稳定视图。标题、说明和按钮使用宿主 Text；确认仅发送用户意图，取消不执行业务操作；列表业务目标在打开时固定。EErrorAlert 接收 Binding<String?>，消息按原文显示，关闭清空，不自动重试。完整示例见 apple/Docs/IOS_DESIGN_SYSTEM.md 与 apple/Examples/IOSControls/。

团队新 iOS 项目通过 `DesignKitIOS` 统一消费 UI 基础件；默认模板入口为 `apple/scripts/new-app.sh --platform ios`。控件主题在 App/独立 scene 根装配，系统版本和通用材质差异留组件内部。原生导航、菜单项、toolbar/alert 与认证品牌控件按平台契约保留。具体边界见 `dwy-ios-development/references/design-system.md`，产品使用与示例查对应版本的 `apple/Docs/UI_FOUNDATION_IMPLEMENTATION.md`、`apple/Examples/IOSControls/`。

iOS/macOS 接入方对已有且满足需求的共享组件必须直接使用，禁止逐个再套同功能包装或复制实现。有业务语义、产品样式或交互组合需求时，在项目 UI 层的 `BusinessUI/`（或既有同职责目录）封装业务基础组件，优先组合共享组件；不存在或不足以支撑业务效果的部分允许用 SwiftUI/UIKit/AppKit 自行实现，并收敛到对应业务组件中，不散写到页面。不必等到多个调用方才封装，也不提前创建无需求的包装。`BizFoundation` 保持纯逻辑，不放 UI；业务服务和任务所有权通过值、Binding 与回调保持原有归属。通用缺口按真实复用收益与改动成本判断是否回流共享库，不强制每次先补库；自行实现部分的系统适配、交互和可访问性由项目负责验证。

按目标平台查 Package.swift、对应公开声明和 apple/README.md，再核对初始化、生命周期、系统版本与错误处理。找不到确切版本时查对应语义化 Git tag；不可用时说明缺口，不以默认分支替代。使用新产品或新增依赖遵守项目选择和授权，不擅自安装。

已采用 `DesignKitMac` 的项目，通用控件、页面组合与平台 UI 入口优先使用基础库公开 API。通用颜色、字号、间距和圆角读取共享主题，不在产品维护第二套默认样式。共享组件的系统版本适配留在基础组件内部；能力缺口按上述业务组件与回流规则处理。原生 `NSAlert`、文件选择器和工具窗口可作为组件内部实现，业务不再分散配置展示细节；文件授权、危险操作、任务取消、权益和持久化仍属于业务。不要机械包装 Text/HStack 等布局原语，也不要将产品导航和品牌几何搬成全体默认值。相关组件以所选版本的 `apple/Docs/Mac-Shared-Compositions.md` 与 `apple/Docs/Mac-Platform-Dialogs.md` 为准。

查到对应版本源码后：同步查 `apple/Docs/SYNC_CORE.md` 与 `apple/Examples/OfflineSync/`；Apple 登录、Google 登录和邮箱密码分别查 `apple/Docs/APPLE_AUTH.md`、`apple/Docs/GOOGLE_AUTH.md`、`apple/Docs/EMAIL_PASSWORD_AUTH.md` 与相应示例。具体文件是否存在以所选 tag 为准。
