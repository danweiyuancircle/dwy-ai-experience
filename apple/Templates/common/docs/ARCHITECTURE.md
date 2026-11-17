# __APP_NAME__ 四层架构

每端内部均为四层，目录与包是组织和编译单位，不增加层级。

| 层 | 位置 | 职责 |
| --- | --- | --- |
| ① App 装配层 | ios/App、macos/App | 入口、DI、路由、scene/window 生命周期 |
| ② Features 功能层 | 本端 Features、BusinessUI；按需产品共享 UI 包 | 页面、页面状态、业务定制 UI |
| ③ BizFoundation 业务基础层 | packages/__APP_NAME__Core/Sources/BizFoundation；按需本端 Platform | 业务规则、模型、协议、服务与平台业务适配 |
| ④ Foundation 通用基础层 | AppleAppKit 实际 products | 跨产品通用能力、基础 UI 与系统适配 |

BusinessUI 属于②，产品专属 Platform 属于③，均不新增第五层。消费项目不建空 Foundation 目录，不以 Foundation 命名 SPM target。只生成所选平台，新增平台不搬已有壳。

## 依赖与生命周期

```text
① App → 本端② Features / BusinessUI → ③ BizFoundation → ④ 非 UI products
① App → 本端③ Platform → ③业务协议
①② → ④ DesignKitIOS / DesignKitMac
可选②产品 UI 包 → ③业务值 / ④对应平台 UI
```

共享 BizFoundation 不依赖 SwiftUI/UIKit/AppKit、DesignKit/DesignCore、StoreKit/PurchaseCore、App 或本端 Platform。App 持有会话、注入平台实现并明确异步任务取消与资源释放；共享核心保留业务协议，不引入具体实现。MainActor 与平台生命周期按 API 契约处理。

Feature 按业务域内聚，不直接访问另一 Feature 的内部页面、ViewModel 或状态；跨域由 App 编排。页面状态留②，应用窗口、导航与 Store 留本端，不把两端壳状态混入 AppShared。

## UI 直接复用与业务定制

- 基础组件已有且满足需求时直接使用，不套同功能包装或复制实现；iOS 使用 DesignKitIOS，macOS 使用 DesignKitMac。
- 业务语义、产品样式或交互组合进入本端 BusinessUI，优先组合共享组件。基础能力不足时允许自行实现所缺部分，UI 收敛在业务组件内，不散写到页面，也不放入共享业务逻辑包。
- 通过值、Binding 与动作回调连接业务，不隐式读取 App 单例或替页面启动任务；权限、权益、持久化、任务和窗口所有权保留原业务/装配层归属。
- 真正双端共同消费且契约稳定时再提为产品 UI 包，不强求触控、键鼠、导航与窗口共用。是否回流通用基础库按真实收益与成本决定，不强制先补库。
- 共享组件通用主题和系统适配归基础库，自行实现部分由项目验证系统适配、交互与可访问性。原生导航、菜单、文件选择和认证品牌控件遵守平台契约。

## 工程与依赖

- 本产品核心位于 packages/__APP_NAME__Core，由本端 project.yml 相对依赖；外部 AppleAppKit 使用已发布、精确锁定版本，不用开发机源码路径。
- 依赖在实际直接消费者的 manifest / project.yml 声明，多处同一外部依赖的约束和已有锁文件保持一致，不为“只写一处”增加转发 target。
- 本端 App sources 收录本端 App、Features、BusinessUI 与资源，不编译另一端或 packages 中的源码。公共实现通过 package product 连接。
- 平台业务实现按需进入本端 Platform：不单独建 target 时显式加入本端 sources；独立建包时新增本端 Package.swift，指定源码 path、相对依赖共享核心并通过 product 引入，不能漏编译或重复编译。
- 包资源使用所属 target bundle；共用资源有唯一来源和明确构建归属，不维护人工同步副本。
- 新应用 iOS/iPadOS 18+、macOS 26+ 与 arm64。已有项目迁移不改数据路径、偏好 key、账号与同步语义，不批量升级依赖。

## 检查与扩展

产品根运行 `python3 scripts/check-architecture.py`，业务单测运行 `swift test --package-path packages/__APP_NAME__Core`；进入已生成平台目录运行 XcodeGen，再进行 SDK 编译和实际交互验收。iOS 的 UI 边界另见 ios/Docs/ARCHITECTURE.md。

新页面放本端 Features，业务定制放本端 BusinessUI，可测试规则放共享核心。新增平台使用基础库生成器的 --add-platform 入口，指定新端 ID，拒绝覆盖已有端并保留核心包与锁定版本。

自动检查覆盖可判定的 import、sources 与版本边界，不能完整判断同 target 的 Feature 互引、同功能包装或生命周期；这些仍需语义审查。生成和单测成功不等于界面、真实设备或生产验收通过。
