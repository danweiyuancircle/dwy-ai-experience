# Apple App Kit（iOS / macOS 应用骨架）

新项目按平台分目录，iOS、macOS 内部均遵循**四层职责**。目录或 SPM 包增加不新增层级：

```
MyApp/
  ios/              # 单平台只生成所选端；双端同时生成 ios 与 macos
    App/            # ① App 装配
    Features/       # ② 功能页面
    BusinessUI/     # ② 业务定制 UI，编入 App
    project.yml
  macos/            # 与 ios 同职责；不编译另一端源码
  packages/MyAppCore/
    Package.swift
    Sources/BizFoundation/  # ③ UI 无关业务核心
    Tests/BizFoundationTests/
  docs/ARCHITECTURE.md
  scripts/check-architecture.py
```

## 四层

| 层 | 目录 | 职责 |
|----|------|------|
| ① | 本端 `App/` | 入口、DI、路由、scene/window 生命周期 |
| ② | 本端 `Features/`、`BusinessUI/`，按需产品 UI 包 | 页面、页面状态、业务定制 UI |
| ③ | 产品核心包、按需本端 `Platform/` | 业务模型、规则、协议、服务与平台业务适配 |
| ④ | AppleAppKit 实际 products | 通用基础能力、基础 UI 与系统适配，不建空层锚点 |

规约：[Docs/ARCHITECTURE.md](Docs/ARCHITECTURE.md)

双端 UI 组件、独立示例与当前验收状态：[apple/Docs/UI_FOUNDATION_IMPLEMENTATION.md](Docs/UI_FOUNDATION_IMPLEMENTATION.md)。规范与 tokens 入口：[apple/Docs/UI_FOUNDATION_PLAN.md](Docs/UI_FOUNDATION_PLAN.md)。

## 部署

权限模块接入、按需产品与宿主配置见 [apple/Docs/Permissions.md](Docs/Permissions.md)，源码纳管审查见 [apple/Docs/Permissions-Upstream-Audit.md](Docs/Permissions-Upstream-Audit.md)，双端宿主示例见 [apple/Examples/Permissions/README.md](Examples/Permissions/README.md)。权限新产品从 0.9.0 起提供；0.8.2 及更早标签不包含这些产品。

| 平台 | 最低版本 |
|------|----------|
| iOS | **18.0+** |
| macOS | **26.0+**（Apple Silicon arm64） |

统一最低支持与逐版本适配、SDK 编译 / 自动化 / 实际交互边界见 [apple/Docs/PLATFORM_COMPATIBILITY.md](Docs/PLATFORM_COMPATIBILITY.md)；适配系统 27 不表示提高最低版本或全量验收通过。

## 生成

以下命令从统一仓库根目录执行。`--platform ios|macos|apple` 分别生成 iOS、macOS、双端形态，统一精确依赖正式版本 `0.10.1`，分别接入 `DesignKitIOS` / `DesignKitMac`；生成工程前须确认该标签可访问。模板不含凭据。

使用现有 Python 3、Swift 6 与 XcodeGen。生成时通过 Swift 前端校验类型名，追加平台通过 SwiftPM 读取已有清单；SDK 编译与运行需要完整 Xcode。工具链未被全局选中时可按命令设置 DEVELOPER_DIR，不要求修改机器的全局选择。

```bash
./apple/scripts/new-app.sh \
  --platform apple \
  --name MyApp \
  --bundle-id com.dwy.myapp \
  --output ~/WebstormProjects \
  --team-id YOURTEAMID

cd ~/WebstormProjects/MyApp
python3 scripts/check-architecture.py
swift test --package-path packages/MyAppCore
python3 -m unittest discover -s ios/Tests -p 'test_*.py'
cd ios
xcodegen generate
open MyApp.xcodeproj
```

iOS App 根注入 `EControlTheme`，已有基础组件满足需求时直接用，不再套同功能包装。业务定制进入本端 BusinessUI，缺口可自行实现并内聚。真正双端共用的业务展示才提为可选产品 UI 包，导航与生命周期各端独立。生成物的结构与 UI 边界检查不替代 SDK 编译、语义审查和设备验收；完整规则见生成项目的 `docs/ARCHITECTURE.md`。

双端初建的 Bundle Identifier 为所传前缀加 `.ios` / `.macos`；单端保留传入 ID。增加另一端时在同一脚本追加 `--add-platform`，保留原 `--name`、`--output`，通过 `--platform ios|macos` 与 `--bundle-id` 指定新端及独立 ID。保留原端、产品核心与已有基础库版本，已有目标拒绝覆盖。macOS 工程进入产品的 macos 目录执行 XcodeGen；单平台不生成未选端。

## 骨架仓（④ 实现）

```
apple/Sources/Shared/       CoreKit LogKit L10nKit CacheKit DesignCore PurchaseCore AuthCore
apple/Sources/iOS/          DesignKitIOS AuthGoogleIOS AuthAppleIOS AuthUI
apple/Sources/macOS/        DesignKitMac
apple/Tests/               通用模块、认证与模板生成回归
apple/Templates/common       共享业务核心、项目规则、文档和检查器
apple/Templates/ios-app|macos-app  平台壳与业务 UI 目录
apple/scripts/new-app.sh
```

所有 iOS/macOS 实现与配套文件统一在 `apple/`；认证代码不再分散在 `modules/auth/`。仓库根 `Package.swift` / `Package.resolved` 保留为远程 SwiftPM 的包入口与依赖锁文件，所有 target 均指向 `apple/`，产品名和调用方式不变。

iOS 与 macOS 分别维护设计规范及平台组件，双端抽取方案见 [apple/Docs/DESIGN_SYSTEMS.md](Docs/DESIGN_SYSTEMS.md)、[apple/Docs/IOS_DESIGN_SYSTEM.md](Docs/IOS_DESIGN_SYSTEM.md) 和 [apple/Docs/MACOS_DESIGN_SYSTEM.md](Docs/MACOS_DESIGN_SYSTEM.md)。根清单与 iOS 模板均支持 iOS 18+。

专业 UI 基础库的完整范围见 [apple/Docs/UI_FOUNDATION_PLAN.md](Docs/UI_FOUNDATION_PLAN.md)，包含 [全局设计 tokens](Docs/DESIGN_TOKENS.md)、[配置与使用规则](Docs/DESIGN_CONFIGURATION.md)、通用组合、可选业务组件及新项目接入验收；这些方案内容尚未全部实现或发布。

第二版方案已补齐 Skill 对照细则和 [首批组件规格](Docs/COMPONENT_SPECIFICATIONS.md)，默认值、状态与事件可作为实施基线。文档复审不代替组件实现、目标系统或消费工程验收。

macOS 26 原型已加入 `DesignKitMac`，包括按钮、菜单、选择、输入与表单。接入及限制见 [apple/Docs/MAC_CONTROLS.md](Docs/MAC_CONTROLS.md)，独立展示源代码位于 `apple/Examples/MacControls/`。原型未发布、ADBox 尚未迁移；窗口边缘下拉、完整辅助功能和 macOS 26 实机验收仍是发布门槛。

邮箱密码登录注册组件选择 `AuthCore` 和 `AuthUI`。接入说明见 `apple/Docs/EMAIL_PASSWORD_AUTH.md`，可运行示例见 `apple/Examples/EmailPasswordAuth/`。

原生 Apple 登录选择 `AuthCore` 和 `AuthAppleIOS`。官方按钮、宿主窗口与会话取消说明见 `apple/Docs/APPLE_AUTH.md`。

远程：https://github.com/danweiyuancircle/dwy-ai-experience.git

业务 App 对**跨仓库基础库只用已发布精确版本**，禁止引用本机源码路径；本产品内部包使用相对 path：

```swift
.package(url: "https://github.com/danweiyuancircle/dwy-ai-experience.git", exact: "0.10.1")
// product 的 package 名是仓库名 dwy-ai-experience
```

每个产品用自己的 `Package.resolved` 钉死 revision。**已上线的 App 默认不升级。**

要不要 bump，只看 [CHANGELOG.md](CHANGELOG.md) 里该版本的 **兼容性** 表（破坏面、不升少什么、要不要改 App）。不要靠读 diff。

改骨架：改本仓 → 先写 CHANGELOG 兼容性四行 → 打 **同号 tag** → 各 App 自己决定是否 bump。0.x 升 minor 视为可破坏。外部基础库不用 `branch: main` 或 `.package(path:)`；各直接消费者的声明与已有锁文件须一致，不为减少声明增加转发层。

业务仓禁止再复制 CoreKit / L10nKit / LogKit。本地若还要自己的日志门面，模块名不能叫 `LogKit`。

## 版本与发版

活文档：[CHANGELOG.md](CHANGELOG.md)。每一节必须写：相对上一版能否不改 App 继续编、不升会少什么、升上来可选/必改项、最低系统。缺一节不准打 tag。

```bash
# 发版（在本仓）
# 1. 改 CHANGELOG：新节置顶，填兼容性表
# 2. git tag 0.x.y && git push origin 0.x.y
# 3. 不要顺手去改已上线 App 的 from:
```

## 自测

```bash
swift test   # 在统一仓库根目录
```
