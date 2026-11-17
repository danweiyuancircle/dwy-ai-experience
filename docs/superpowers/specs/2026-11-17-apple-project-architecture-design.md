# Apple 项目基础分包架构方案

状态：用户已确认并授权实施；明确两端内部仍为四层。规范与生成器已落地，实际验收见 `docs/superpowers/reports/2026-11-17-apple-project-architecture-validation.md`；ADBox 本轮只做对齐审计，不迁移源码。

四层固定为① App 装配、② Features（含 BusinessUI）、③ BizFoundation（含本产品平台业务适配）、④ Foundation（AppleAppKit 实际产品）。下文中的平台目录、共享包和可选 UI 包是组织或编译单位，不新增架构层。

## 1. 目标与选择

为团队 iOS、macOS、iOS + macOS 项目提供同一套职责划分、目录约定、依赖边界和创建入口。新项目按模板生成，已有项目按实际改动逐步对齐。

沿用已确认的 UI 规则：共享组件满足需求时直接使用，接入方不再套同功能包装；业务定制集中在项目业务基础组件，缺口可自行实现，不强制先改共享库。

比较三种方案：

| 方案 | 收益 | 成本 / 限制 | 建议 |
| --- | --- | --- | --- |
| 单平台保留根 App/Features，双平台再搬到平台目录 | 单端目录最少 | 后续加平台要迁目录，两套生成与规范容易分叉 | 不采用 |
| 所有项目使用平台目录 + 本产品共享业务包，其他包按需增加 | 单双端结构一致，增加平台不搬已有壳，边界可由 target 验证 | 单端多一层平台目录 | 推荐 |
| 每个 Feature、服务、UI 都拆独立 SPM 包 | 编译隔离细 | 初始清单、资源、可见性和依赖管理负担大 | 不作为默认 |

统一的是职责与依赖，不要求每个项目拥有相同数量的包；不强制迁移已有目录名，不创建无实际用途的模块。

## 2. 标准目录

以下为双平台完整形态。仅 iOS 时不生成 macos；仅 macOS 时不生成 ios。标注“按需”的部分没有需求就不生成。

```text
<Product>/
  AGENTS.md
  README.md
  ios/
    App/                         # 入口、依赖装配、路由、scene 生命周期
    Features/
      Settings/                  # 一个业务域内放 View、状态与本域逻辑
    BusinessUI/                  # 业务定制 UI，编入本端 App target
    Platform/                    # 按需：iOS 专属服务与系统适配
    Package.swift                # 按需：定义本端独立 Platform target
    Resources/
    Tests/
    UITests/
    project.yml
  macos/
    App/
    Features/
      Settings/
    BusinessUI/
    Platform/                    # 按需：macOS 专属服务与系统适配
    Package.swift                # 按需：定义本端独立 Platform target
    Resources/
    Tests/
    UITests/
    project.yml
  packages/
    <Product>Core/
      Package.swift
      Sources/
        BizFoundation/           # 本产品业务模型、规则、协议与共享业务服务
      Tests/
        BizFoundationTests/
    <Product>UI/                 # 按需：已有双端共同消费的业务 UI / 品牌契约
      Package.swift
      Sources/
        <Product>UI/
      Tests/
  resources/                     # 按需：确实共用的资源，明确唯一归属
  docs/
    ARCHITECTURE.md
    TEST_CASES.md
  scripts/
    check-architecture.py
```

`<Product>Core` 是包名，`BizFoundation` 是默认业务逻辑 target。现有项目已有稳定名称时保留，不为统一名称制造迁移。业务复杂后可在同一包内增加有明确职责的 target，不必每个 target 都另开包。

`BusinessUI` 是 App 内目录，不是基础控件的代理层。空模板只提供职责说明和工程收录配置，不创建示例包装组件或空 SPM target。

不再要求消费项目放一个无实现的 Foundation 目录作为层锚点；共享基础层由真实的 AppleAppKit package 产品依赖表达。SPM target 不得命名为 Foundation，以免与系统框架冲突。

## 3. 职责与依赖

| 部分 | 应放内容 | 不放内容 |
| --- | --- | --- |
| AppleAppKit | 跨产品通用能力、基础 UI、通用系统适配 | 本产品实体、品牌几何、产品路由和业务单例 |
| BizFoundation | 本产品模型、业务规则、能力协议、UI 无关业务服务 | SwiftUI/UIKit/AppKit、窗口导航、应用入口、另一端专属实现 |
| Platform | 系统能力的具体实现，按协议连接业务 | 页面布局、跨端公共规则、另一端实现 |
| BusinessUI | 产品卡片、业务表单、定制交互与绘制 | 同功能控件代理、隐式访问 App 单例、擅自启动业务任务 |
| Features | 完整业务域的页面、页面状态与本域操作 | 其他 Feature 的页面/内部状态、其他平台壳源码 |
| App | 初始化、依赖注入、路由与 scene/window 生命周期 | 逐渐堆积的业务算法、基础控件实现 |

```text
App ──→ 本端 Features ──→ 本端 BusinessUI ──→ DesignKitIOS / DesignKitMac
 │           │                    └──────→ BizFoundation（按需读取业务值）
 │           └───────────────────────────→ BizFoundation
 ├────→ 本端 Platform ───────────────────→ BizFoundation 协议
 └────→ AppleAppKit 公开产品

可选 ProductUI ──→ DesignCore / 对应平台 DesignKit / BizFoundation
BizFoundation ──→ AppleAppKit 的非 UI 产品及确有需要的非 UI 依赖
```

- 业务协议归业务消费者所在模块；App 创建 Platform 实现后注入，业务核心不依赖具体 Platform target。
- Platform 仅在存在真实系统差异或隔离需求时建立 target。单平台同样允许存在平台专属实现，不以“只有一端”为理由放进业务核心。建立独立 target 时，在本端新增 Package.swift，以显式 path 指向 Platform 内源码，通过相对路径依赖 ProductCore，由本端 project.yml 引用其 product；尚不需要独立 target 的实现留在本端 Platform 目录，并显式加入本端 App sources。
- 本端 App 与 Feature 可以直接使用满足需求的共享 UI，无须经过 BusinessUI 转发。
- Feature 之间不直接引用内部页面、ViewModel 或状态；跨域由 App 编排，确有共享规则再放业务核心。不要求每个 Feature 建包，源码同 target 时边界通过检查与审查共同维护。
- 页面展示状态留在 Feature，应用连接/会话/路由状态由本端 App 装配并持有；可共用状态转换规则，不能把两端 Store 塞进 AppShared 追求代码去重。
- App/window/scene 范围、异步任务取消和服务释放在装配入口写清；UI 与平台 UI 操作按 MainActor 契约执行，不能仅按文件夹判断线程安全。
- 原生导航、菜单、文件选择与系统认证控件遵守平台契约，不强制替换成自绘组件。

## 4. 业务 UI 的落点

按顺序判断：

1. 共享组件已经满足需求：直接用，不新建包装。
2. 出现产品专用外观、业务语义或交互组合：放本端 BusinessUI，优先组合共享组件；不必等到第二个调用方。
3. 共享组件能力不足：自行实现所缺部分，但收敛到对应业务组件，验证系统适配和可访问性。
4. 双端已经共同需要、输入与交互契约稳定：可提到 ProductUI；只共享真实相同的部分，导航、窗口、触控和键鼠保持各端实现。
5. 已证实跨产品通用：再评估是否进入 AppleAppKit，按授权、收益与迁移成本决定。

例如：设备实体和连接规则放 BizFoundation；连接传输实现放各端 Platform；设备卡展示放各端 BusinessUI；页面决定何时连接；App 持有会话并处理退出。两端设备卡完全相同的状态文案与展示片段可放 ProductUI，不强求整张卡跨端一致。

共享 ProductUI 是可选业务能力包，不是强制的第二套通用 DesignKit；禁止为了统一入口把每个 AppleAppKit 控件重新导出为产品控件。

## 5. 三种项目形态与生成

| 类型 | 初始生成 | 不生成 |
| --- | --- | --- |
| iOS | ios + ProductCore + 文档和检查 | macos、ProductUI、无需求的平台 target |
| macOS | macos + ProductCore + 文档和检查 | ios、ProductUI、无需求的平台 target |
| 双平台 | ios + macos + 同一份 ProductCore + 文档和检查 | 无实际共用展示的 ProductUI、空适配包 |

拟扩展现有 `apple/scripts/new-app.sh`，保留 `--platform ios`、`--platform macos`，新增 `--platform apple` 表示一次创建双端。新结构对旧模板的目录变化必须在脚本帮助与模板文档明确说明，不静默覆盖已有输出目录。

新建项目后能够直接：生成对应 Xcode 工程、运行业务包测试、运行架构检查、构建所选平台。双平台可生成 workspace 汇总工程；workspace 只组织工程，不改变依赖与源码归属。不新增另一套脚手架工具。

以后补平台：保留原平台目录，增加目标平台壳，复用同一份 ProductCore；按业务实现相应 Platform 与页面。增加平台的命令必须检查已有文件，不能重建或覆盖原项目。

## 6. 工程、依赖与资源

- 产品内部真实 SPM 包使用相对 path 依赖；跨仓库的 AppleAppKit 使用已发布、精确锁定的版本，不引用开发机绝对路径。
- 依赖只在实际直接消费它的 manifest 或 XcodeGen 配置声明。App 直接使用 DesignKit 时保留直接产品依赖，不为减少版本声明而增加转发 target 或包装控件。
- 同一外部依赖跨 manifest / project.yml 出现时，版本约束必须一致；生成时写入同一选定版本，检查器校验声明与锁文件。不能继续并存“版本只能写根 Package.swift”与模板实际重复声明的矛盾规则。
- 默认各端 App target 只收录本端 App、Features、BusinessUI 与资源。新增 Platform 实现时二选一：未建立 SPM target 则将本端 Platform 显式加入 App sources；建立 SPM target 则只通过 package product 接入，不重复编译其源码。检查器须拒绝漏收录和重复收录。
- macOS 不点名编译 ios 的源码，iOS 不编译 macos；公共实现通过 package product 引用，不靠同一 Swift 文件同时挂到两端 sources。
- 包资源使用所属 target bundle；共用资源明确唯一来源、构建时按使用目标收录，不产生两份人工维护的同名资源。资源加载通过已有本地化与资源机制完成，不另造资源管理框架。
- 新项目系统基线沿用当前平台规范：iOS/iPadOS 18+；macOS 26+、Apple Silicon。共享包平台声明按实际消费者设置；macOS 上的业务单测不能代替 iOS SDK 编译。

## 7. ADBox 对齐方式

已核实 ADBox 当前结构：

| 当前入口 | 对应职责 | 对齐建议 |
| --- | --- | --- |
| packages/ADBoxCore | 共享业务包：BizFoundation、ADBoxCloud、ClientLog | 保留，不另建重复核心包 |
| packages/ADBoxUI | 共享品牌和业务展示，现有 DesignKit / ADBoxUI 产品 | 保留已有有效组合；逐项判断有无纯转发，不先整体删除或重命名 |
| ios/App、ios/Features | iOS 装配与功能 | 保留 |
| ios/Platform/IOSPlatform | iOS 专属适配 | 保留平台隔离 |
| macos/App、macos/Features | Mac 装配与功能 | 保留 |
| macos/Platform/MacFoundation | Mac 专属适配 | 保留名称与公共调用，不为统一命名重写 |
| ios/UI、macos/UI | 当前平台 UI，包含 IOSUI / MacUI | 按实际职责视为 BusinessUI，不要求先搬目录 |

ADBox 属于标准双平台形态，不另立例外架构。它已有的额外业务包、平台 target 和资源随业务需要保留；新项目不照搬 ADB、插件、TLS、云同步等无关能力。

后续迁移先盘点调用与生命周期，再对同功能包装、散落业务 UI、跨端源码引用逐项处理。公开符号、包产品、数据模型、存储路径、偏好 key、账号与同步语义不能因目录调整改变；不借架构迁移清空用户数据或批量升级依赖。

## 8. 规范落地范围

确认后，按以下顺序实施：

1. **统一规范**：更新 `apple/Docs/ARCHITECTURE.md`、`apple/Docs/LAYERING.md`、Apple 架构 Skill 的 layering/extraction 资料及 iOS/macOS 接入资料，消除旧分层与版本规则冲突。
2. **生成模板**：更新 `apple/Templates` 和 `apple/scripts/new-app.sh`，支持三种形态；同步帮助、README、生成物架构说明及工程 sources。
3. **自动验证**：扩展 `apple/Tests/test_templates.py` 与 `apple/Tests/TEST_CASES.md`，让生成结果而非模板字符串成为主要验收对象。
4. **ADBox 对齐审计**：输出实际差异、调用影响与迁移顺序；在其仓库另行确认具体改造范围后实施，不把这份方案视为已迁移。

本次方案不包含发布、修改全局已安装 Skills、所有历史项目批量搬目录或新增运行时依赖。各项目后续按统一规范创建和评审，不承诺无人触发的后台巡检。

## 9. 验证与验收标准

| 边界 | 验证 |
| --- | --- |
| 三种模板可用 | 临时目录真实生成，XcodeGen 成功，选定平台的 App target 构建通过 |
| 业务核心独立 | ProductCore 单测可单独运行；拒绝 UI / App / 平台实现反向依赖 |
| 平台隔离 | 检查工程 sources 与 package targets；注入另一端源码/依赖时必须失败 |
| 业务 UI 进入工程 | 注入业务组件后，生成工程确实纳入本端编译 sources；不是只生成目录 |
| UI 复用边界 | 自动检查可判定的 API 越界；同功能包装、组件是否应共享由语义审查确认，不能声称正则能完整判断 |
| 依赖一致 | 各声明和锁文件对应同一选定版本；不同步时明确失败，不自动改锁掩盖问题 |
| 生命周期与资源 | 最小宿主启动、导航、主题/语言、资源加载、关闭与任务释放按实际平台验证 |
| 既有项目迁移 | 先建立现有测试基线，迁移后回归实际入口；目录变化不代表业务与设备验收通过 |

架构检查优先复用 SwiftPM、XcodeGen 与已有 Python 检查；不写自制 Swift 解析器，不为实现目录规范引入框架。自动化不能覆盖的源码语义和实际交互必须单独报告。

## 10. 本次调查与限制

已读取当前单平台模板、生成器调用入口、Apple 架构 Skill，并核对 ADBox 的四份 package manifest、平台工程 sources 与项目边界约定。ADBox 已有共享业务、共享 UI 与平台实现，能支撑上述映射。

本方案的模板、规范与架构检查已进入实施；具体执行证据以验收记录为准。尚未进行 ADBox 全量调用审计、迁移或目标设备验收；不把已有包的存在视为其全部内部边界已经符合新规范。
