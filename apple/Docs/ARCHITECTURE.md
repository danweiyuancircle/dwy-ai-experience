# Apple 项目四层架构规约

iOS、macOS 与双平台应用遵循同一套四层架构。**层是职责和依赖方向，目录与 SPM 包是组织和编译单位；增加平台或包不增加层级。**

新项目最低支持 iOS/iPadOS 18、macOS 26（Apple Silicon arm64），使用 Swift 6。既有项目按已确认范围迁移，不因采用本规范自动升级系统下限、依赖或重命名公开模块。

## 1. 四层职责

| 层 | 落点 | 职责 | 边界 |
| --- | --- | --- | --- |
| ① App 装配层 | `ios/App`、`macos/App` | 入口、DI、路由、scene/window 生命周期、签名与打包装配 | 不堆积业务算法或基础控件实现 |
| ② Features 功能层 | 本端 `Features/<Name>`、`BusinessUI`，按需产品共享 UI 包 | 页面、页面状态、业务展示和定制交互 | 不引用另一 Feature 内部页面或另一平台壳 |
| ③ BizFoundation 业务基础层 | `packages/<Product>Core/Sources/BizFoundation`、按需本端 `Platform` | 本产品模型、规则、协议、业务服务和平台业务适配 | 共享核心不依赖 UI、App 或具体平台实现 |
| ④ Foundation 通用基础层 | AppleAppKit 实际 package products | 跨产品通用能力、基础 UI、通用系统适配 | 不依赖产品实体、业务单例或产品路由 |

BusinessUI 属于②，不是第五层；产品专属的 IOSPlatform、MacFoundation 等属于③的平台实现，也不是第五层。与产品无关的系统适配可归④，由通用基础库承载。SPM target 禁止命名为 Foundation，避免与系统框架冲突；消费项目无需建立无实现的 Foundation 层锚点目录。

## 2. 新项目目录

```text
<Product>/
  AGENTS.md
  README.md
  ios/                          # 仅生成所选平台
    App/
    Features/<Name>/
    BusinessUI/                 # 编入本端 App target
    Platform/                   # 按需：本端业务适配
    Package.swift               # 按需：本端平台 target
    Resources/
    Tests/
    UITests/
    project.yml
  macos/                        # 仅生成所选平台；内部职责与 ios 一致
    App/
    Features/<Name>/
    BusinessUI/
    Platform/                   # 按需
    Package.swift               # 按需
    Resources/
    Tests/
    UITests/
    project.yml
  packages/
    <Product>Core/
      Package.swift             # 产品包名；默认 target 为 BizFoundation
      Sources/BizFoundation/
      Tests/BizFoundationTests/
    <Product>UI/                # 按需：真实双端共用业务 UI / 品牌契约
  resources/                    # 按需：明确唯一来源的共用资源
  docs/ARCHITECTURE.md
  scripts/check-architecture.py
```

单平台只生成 ios 或 macos，业务核心仍独立成包，后续增加另一端不搬动已有壳。Feature 按业务域分目录，不按全局 Views/ViewModels 横切，不要求每个 Feature 都成为 SPM 包。按需目录没有实际实现时不创建空 target。

## 3. 依赖方向

```text
① App → 本端② Features / BusinessUI → ③ BizFoundation → ④ 非 UI 基础产品
① App → 本端③ Platform → ③ BizFoundation 协议
① App / ② Features / BusinessUI → ④ DesignKitIOS 或 DesignKitMac
按需② ProductUI → ③业务值 / ④ DesignCore 与对应平台 UI
```

- App 创建并注入平台实现；业务核心只定义所需协议，不引用具体 Platform target。应用会话、Store、导航与窗口状态由本端持有，不建立 AppShared 把两端壳状态混入业务核心。
- 共享 BizFoundation 禁止依赖 SwiftUI、UIKit、AppKit、StoreKit、DesignCore、DesignKit、PurchaseCore、App 或本端 Platform；认证/同步等 UI 无关业务服务可使用实际需要的非 UI 产品。
- 本端 Platform 可为真实系统能力使用相应系统框架，但不承载页面布局或跨端共同规则；MainActor、权限、任务取消、资源释放与窗口归属按实际 API 契约处理。
- Feature 不直接访问另一 Feature 的内部页面、ViewModel 或状态；跨域由 App 编排，真实共享规则再进入③。同 target 的源码边界仍需语义审查，不将文件夹当作编译隔离。
- 不编译另一端壳源码，不将同一公共 Swift 实现手工挂到两端 sources；公共实现通过 package product 引用。

## 4. UI 直接复用与业务定制

1. iOS 使用 DesignKitIOS，macOS 使用 DesignKitMac。已有且满足需求的共享组件直接使用，禁止逐个再套同功能包装或复制实现。
2. 有业务语义、产品样式或交互组合时，在本端 BusinessUI（既有项目可沿用同职责目录）封装业务基础组件，优先组合共享组件；不必等到第二个调用方，也不提前建无需求的包装。
3. 共享组件缺失或不足时，允许自行实现所缺部分，UI 收敛在对应业务组件，不散写到页面。通过值、Binding 和动作回调接入，服务、权限、权益、持久化和任务所有权仍由业务/装配层持有。
4. 真实双端共同需要且契约稳定的部分，可提到产品 UI 包；导航、窗口、触控、键鼠不强求共用。产品 UI 包属于②，不是第二套通用控件库或强制转发入口。
5. 通用缺口是否回流 AppleAppKit 按真实复用收益和改动成本决定，不强制先补库。共享组件系统适配留库内，自行实现部分由项目验证系统适配、交互和可访问性。

通用主题读取基础库公开接口，品牌配置保留产品归属；原生导航、菜单、文件选择与认证品牌控件保留平台契约，不机械包装布局原语或所有原生 Button。

## 5. 工程、版本与资源

- 产品内包使用相对 path；外部 AppleAppKit 使用已发布、精确锁定版本，不引用开发机源码路径。根工作区没有重复业务核心副本。
- 依赖在真正直接消费者的 manifest / project.yml 声明。同一外部依赖多处出现时约束必须一致，已有锁文件匹配所选版本；允许真实重复声明，不为“只写一处”增加转发 target 或控件包装。
- App sources 收录本端 App、Features、BusinessUI 和资源。Platform 未建包时显式加入本端 sources；建为包时只通过 product 引用，禁止漏编译或重复编译。
- 包资源使用所属 target bundle；共用资源明确唯一来源与各端收录方式，不维护人工同步副本。
- 四层规范由模板、架构 Skill、生成物检查和审查共同执行；静态检查不能代替 Swift 语义分析、实际编译与目标系统交互。

## 6. 创建、扩展与既有项目

入口为 `apple/scripts/new-app.sh --platform ios|macos|apple`。apple 一次创建双端，传入的 bundle-id 为前缀，分别追加 .ios、.macos；单端保留传入 ID。

追加平台使用同一入口的 `--add-platform`，同时指定 `--platform ios|macos`、原产品 `--name`、新端独立 `--bundle-id` 和原输出父目录 `--output`。保留业务核心、依赖版本与原平台文件；已有目标目录时拒绝覆盖。旧结构先核对实际清单与迁移范围，不能直接假定符合新模板。

ADBox 等既有项目保留有效包名、目录与对外符号，按职责映射四层；不为规范化改变存储路径、偏好 key、同步语义、账号或用户数据。不自动全仓搬迁、发布或更新全局已安装 Skills。
