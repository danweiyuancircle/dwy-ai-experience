# Apple 四层架构与依赖

先核对实际目录、清单、调用与目标平台。新项目用团队模板，既有项目按授权对齐，不因启用 Skill 重建工程、升级系统下限或重命名公开模块。系统版本与架构见 dwy-ios-development、dwy-macos-development。

## 四层，不以包数量定义层数

| 层 | 职责 | 新项目落点 |
| --- | --- | --- |
| ① App 装配层 | 入口、DI、路由、scene/window 生命周期 | `ios/App`、`macos/App` |
| ② Features 功能层 | 页面、页面状态、业务 UI 与交互 | 本端 `Features/<Name>`、`BusinessUI`，按需产品 UI 包 |
| ③ BizFoundation 业务基础层 | 本产品规则、模型、协议、业务服务和平台业务适配 | `packages/<Product>Core/Sources/BizFoundation`，按需本端 `Platform` |
| ④ Foundation 通用基础层 | 跨产品能力、基础 UI 与通用系统适配 | AppleAppKit 实际 products |

BusinessUI 属于②，产品专属 Platform 属于③；单端、双端均不新增第五层。纯通用系统适配可归④，但不得含产品实体或壳状态。目录与 SPM target 是组织/编译单位，不要求一层恰好一个包。消费项目不建空 Foundation 层锚点，target 不得命名 Foundation，避免与系统框架冲突。

## 标准形态

```text
ios/                         # 单端只生成所选平台
  App/
  Features/<Name>/
  BusinessUI/                 # 编入 App，不是强制包装层
  Platform/                  # 按需
  Package.swift              # 按需：独立平台 target
  project.yml
macos/                       # 双端增加同职责目录，不编译 ios 源码
packages/
  <Product>Core/
    Package.swift
    Sources/BizFoundation/
    Tests/BizFoundationTests/
  <Product>UI/                # 按需：真实双端共用业务 UI
docs/ARCHITECTURE.md
scripts/check-architecture.py
```

ProductCore 是产品包名，默认逻辑 target 为 BizFoundation。Feature 按完整业务域聚合，不按全局 Views/ViewModels 横切，默认不逐个拆包。已有项目保留稳定模块名和目录，以职责映射，不为改名破坏调用方。

## 依赖与生命周期

```text
① App → 本端② Features / BusinessUI → ③ BizFoundation → ④ 非 UI products
① App → 本端③ Platform → ③业务协议
①② → 本端④ DesignKit
可选② ProductUI → ③业务值 / ④ DesignCore 与对应平台 UI
```

- 共享 BizFoundation 不依赖 SwiftUI/UIKit/AppKit、DesignKit/DesignCore、StoreKit/PurchaseCore、App 或具体 Platform 实现；按业务需求使用非 UI 基础产品。
- App 创建平台实现并通过业务协议注入。平台业务适配可使用实际所需系统框架，不放 UI 页面或跨端共同规则；任务、会话、权限与资源释放保留明确 owner。MainActor 与并发契约按 API 决定，不凭目录推断线程安全。
- Platform 不独立建 target 时加入本端 App sources；需要隔离时由本端 Package.swift 定义 target、相对依赖产品核心，通过 product 引入，不能漏编译或重复编译。
- Feature 不引用其他 Feature 内部页面、ViewModel 或状态，跨域由 App 编排或③协议连接。共享规则有真实需求才上提，不把两端 Store、导航、窗口与连接状态塞入 AppShared。
- 另一平台 App、Features、业务 UI 与平台实现不得成为本端 sources。公共实现通过 package product 引入，不用两端手工收录同一源码绕开边界。

## UI 复用

满足需求的共享组件直接用，禁止逐个再套同功能包装或复制实现。业务语义、产品样式或交互组合放② BusinessUI，优先组合基础组件；能力不足可自行实现所缺部分，收敛到业务组件内。业务 UI 不放共享③；不必等多个调用方，也不提前建无需求的包装。

双端已有共同需求且契约稳定时才提为产品 UI 包，不强求触控、键鼠、导航和窗口一致。共享组件通用适配归④，自行实现由项目验证系统适配与可访问性；是否回流通用库按收益和成本决定，不强制先改库。

## 工程、版本与检查

- 产品内包用相对 path，跨仓库基础库用已发布精确版本，不引用本机绝对源码路径。
- 依赖在真正直接消费者的 manifest / project.yml 声明。多处同一依赖约束必须一致，已有锁文件匹配所选版本；允许真实重复声明，不为“只写一处”增加转发 target 或控件包装。
- 共用资源有唯一来源和明确 bundle 归属；系统平台产品按实际需要链接，不默认引入所有能力。
- 创建入口 `apple/scripts/new-app.sh --platform ios|macos|apple`；追加另一端用 --add-platform，保留原端与核心包，不覆盖已有目录、不自动升级依赖。
- 结构、import、sources、清单与版本可自动检查；同 target 的 Feature 互引、同功能包装和生命周期仍需语义审查。生成、编译、单测与实际交互分别报告，不把静态检查称为设备验收。
