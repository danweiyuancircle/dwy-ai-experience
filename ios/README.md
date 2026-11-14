# Apple App Kit（iOS / macOS 应用骨架）

生成业务工程时**根目录并列四层**（对齐 TVRemote）：

```
MyApp/
  App/              # ① APP 层
  Features/         # ② Features 层
  BizFoundation/    # ③ 业务基础层
  Foundation/       # ④ 业务无关基础层（层锚点；kits → 统一私有包版本）
  Resources/
  Package.swift
  project.yml
  Docs/ARCHITECTURE.md
```

## 四层

| 层 | 目录 | 职责 |
|----|------|------|
| ① | `App/` | 入口、根路由、Info、打包 |
| ② | `Features/` | 子功能 UI 分包 |
| ③ | `BizFoundation/` | 领域纯逻辑 |
| ④ | `Foundation/` | 业务无关基建（实现在骨架仓） |

规约：[Docs/ARCHITECTURE.md](Docs/ARCHITECTURE.md)

双端 UI 组件、独立示例与当前验收状态：[ios/Docs/UI_FOUNDATION_IMPLEMENTATION.md](Docs/UI_FOUNDATION_IMPLEMENTATION.md)。规范与 tokens 入口：[ios/Docs/UI_FOUNDATION_PLAN.md](Docs/UI_FOUNDATION_PLAN.md)。

## 部署

| 平台 | 最低版本 |
|------|----------|
| iOS | **18.0+** |
| macOS | **26.0+**（Apple Silicon arm64） |

统一最低支持与逐版本适配、SDK 编译 / 自动化 / 实际交互边界见 [ios/Docs/PLATFORM_COMPATIBILITY.md](Docs/PLATFORM_COMPATIBILITY.md)；适配系统 27 不表示提高最低版本或全量验收通过。

## 生成

以下命令从统一仓库根目录执行。iOS 新项目精确依赖已发布的 `0.8.0-beta.4`，默认接入 `DesignKitIOS`；macOS 模板仍保留原有 `0.4.1` 基线。模板不含凭据。

```bash
./ios/scripts/new-app.sh \
  --platform ios \
  --name MyApp \
  --bundle-id com.dwy.myapp \
  --output ~/WebstormProjects \
  --team-id YOURTEAMID

cd ~/WebstormProjects/MyApp
ls   # 应看到 App Features BizFoundation Foundation
xcodegen generate
open MyApp.xcodeproj
python3 -m unittest discover -s Tests -p 'test_*.py'
```

iOS App 根注入 `EControlTheme`，设置页直接使用 E 组件。品牌和业务组合留项目内，通用控件的 iOS 18 / 26 差异由基础库处理；原生导航、系统 toolbar/alert、菜单项与认证品牌控件保留系统契约。生成物中的边界测试检查版本一致、iOS 平台依赖、主题入口和页面材质越界，不代替实际编译与设备验收。具体边界见生成项目的 `Docs/ARCHITECTURE.md`。

## 骨架仓（④ 实现）

```
ios/Sources/Shared/       CoreKit LogKit L10nKit CacheKit DesignCore PurchaseCore AuthCore
ios/Sources/iOS/          DesignKitIOS AuthGoogleIOS AuthAppleIOS AuthUI
ios/Sources/macOS/        DesignKitMac
ios/Tests/               通用模块、认证与模板生成回归
ios/Templates/ios-app|macos-app
ios/scripts/new-app.sh
```

所有 iOS/macOS 实现与配套文件统一在 `ios/`；认证代码不再分散在 `modules/auth/`。仓库根 `Package.swift` / `Package.resolved` 保留为远程 SwiftPM 的包入口与依赖锁文件，所有 target 均指向 `ios/`，产品名和调用方式不变。

iOS 与 macOS 分别维护设计规范及平台组件，双端抽取方案见 [ios/Docs/DESIGN_SYSTEMS.md](Docs/DESIGN_SYSTEMS.md)、[ios/Docs/IOS_DESIGN_SYSTEM.md](Docs/IOS_DESIGN_SYSTEM.md) 和 [ios/Docs/MACOS_DESIGN_SYSTEM.md](Docs/MACOS_DESIGN_SYSTEM.md)。根清单与 iOS 模板均支持 iOS 18+。

专业 UI 基础库的完整范围见 [ios/Docs/UI_FOUNDATION_PLAN.md](Docs/UI_FOUNDATION_PLAN.md)，包含 [全局设计 tokens](Docs/DESIGN_TOKENS.md)、[配置与使用规则](Docs/DESIGN_CONFIGURATION.md)、通用组合、可选业务组件及新项目接入验收；这些方案内容尚未全部实现或发布。

第二版方案已补齐 Skill 对照细则和 [首批组件规格](Docs/COMPONENT_SPECIFICATIONS.md)，默认值、状态与事件可作为实施基线。文档复审不代替组件实现、目标系统或消费工程验收。

macOS 26 原型已加入 `DesignKitMac`，包括按钮、菜单、选择、输入与表单。接入及限制见 [ios/Docs/MAC_CONTROLS.md](Docs/MAC_CONTROLS.md)，独立展示源代码位于 `ios/Examples/MacControls/`。原型未发布、ADBox 尚未迁移；窗口边缘下拉、完整辅助功能和 macOS 26 实机验收仍是发布门槛。

邮箱密码登录注册组件选择 `AuthCore` 和 `AuthUI`。接入说明见 `ios/Docs/EMAIL_PASSWORD_AUTH.md`，可运行示例见 `ios/Examples/EmailPasswordAuth/`。

原生 Apple 登录选择 `AuthCore` 和 `AuthAppleIOS`。官方按钮、宿主窗口与会话取消说明见 `ios/Docs/APPLE_AUTH.md`。

远程：https://github.com/danweiyuancircle/dwy-ai-experience.git

业务 App **只许版本依赖，禁止 path / 源码目录**：

```swift
.package(url: "https://github.com/danweiyuancircle/dwy-ai-experience.git", from: "0.4.1")
// product 的 package 名是仓库名 dwy-ai-experience
```

每个产品用自己的 `Package.resolved` 钉死 revision。**已上线的 App 默认不升级。**

要不要 bump，只看 [CHANGELOG.md](CHANGELOG.md) 里该版本的 **兼容性** 表（破坏面、不升少什么、要不要改 App）。不要靠读 diff。

改骨架：改本仓 → 先写 CHANGELOG 兼容性四行 → 打 **同号 tag** → 各 App 自己决定是否 bump。0.x 升 minor 视为可破坏。不要 `branch: main`，不要 `.package(path:)`。

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
