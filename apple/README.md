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

## 部署

| 平台 | 最低版本 |
|------|----------|
| iOS | **17.0+** |
| macOS | **14.0+** |

## 生成

以下命令从统一仓库根目录执行；0.4.1 tag 发布后，生成项目才能远端解析该版本。私有仓库访问通过开发者现有 Git 认证完成，模板不含凭据。

```bash
./apple/scripts/new-app.sh \
  --platform ios \
  --name MyApp \
  --bundle-id com.dwy.myapp \
  --output ~/WebstormProjects \
  --team-id U969S59QT8

cd ~/WebstormProjects/MyApp
ls   # 应看到 App Features BizFoundation Foundation
xcodegen generate
open MyApp.xcodeproj
```

## 骨架仓（④ 实现）

```
apple/Sources/Shared/     CoreKit LogKit L10nKit CacheKit DesignCore PurchaseCore
apple/Sources/iOS/        DesignKitIOS
apple/Sources/macOS/      DesignKitMac
modules/auth/apple/Sources/ AuthCore AuthGoogleIOS
apple/Templates/ios-app|macos-app
```

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
