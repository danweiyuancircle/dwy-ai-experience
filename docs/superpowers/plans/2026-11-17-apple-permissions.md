# Apple 权限库实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 AppleAppKit 中维护可复用的 iOS、macOS 权限能力，减少各产品重复处理授权、设置跳转和恢复流程。

**Architecture:** iOS 以上游 PermissionsKit 为基础，macOS 以上游 PermissionFlow 为基础；保留可追溯的第三方源码，公开团队自有接口。共享权限语义，平台实现及 UI 分离；权限请求、设置引导、文件访问生命周期分别建模。

**Tech Stack:** Swift、SwiftPM、Apple 原生权限 API、SwiftUI/AppKit/UIKit；沿用项目 iOS 18+、macOS 26+（Apple Silicon）基线。

**Spec:** 本文“需求与边界”记录本轮用户需求，作为本计划的内嵌规格。

## 需求与边界

- 用户要求拉取源码、自行维护、先审查再封装，以供其他 iOS/macOS 项目复用。
- iOS 暂按上一轮推荐的 PermissionsKit 解释，不是 PermissionsSwiftUI；执行时明确告知这一假设。
- 本轮交付计划；源码拉取、审查和实现均为以下待执行步骤，不能视为已经完成。
- 本期完成两端权限库、必要引导 UI、示例、文档和测试；ADBox 作为首个业务验收对象，业务迁移在基础库可用后进行。
- 不自动发布、不推送、不改系统隐私设置、不重置测试设备数据，不改现有不相关工作区内容。
- 完整拉取并盘点两份源码；逐项标注“已支持／平台不支持／待适配”，不得用统一成功返回掩盖缺口。

## 当前核实与风险

- AppleAppKit 根 `Package.swift` 使用 swift-tools-version 6.0，部署基线为 iOS 18、macOS 26。
- PermissionsKit 当前 main 清单使用 Swift 6.3，声明 iOS/tvOS/watchOS/macOS；包含相机、照片、通知、麦克风、日历、联系人、提醒、语音、定位、运动、媒体库、蓝牙、跟踪、Face ID、Siri、健康等模块。清单声明不等于每种能力可在所有平台运行。
- PermissionFlow 当前 main 清单使用 Swift 6.1，分为系统设置跳转、权限引导和按能力拆分的状态模块。
- 前述为在线清单核查，尚未完整审计源码、验证发布版本或编译。
- 两个上游标注 MIT；源码引入时必须核对实际 LICENSE 及每份保留代码的声明。
- 不直接降低上游 tools-version。先验证本机和 CI 工具链，再选择兼容的稳定版本；必须使用主干修复时锁定 commit 并记录理由。

来源：
- https://github.com/sparrowcode/PermissionsKit
- https://github.com/jaywcjlove/PermissionFlow
- https://developer.apple.com/documentation/technotes/tn3179-understanding-local-network-privacy

## Global Constraints

- 默认在主目录 develop 工作，不新增分支或 worktree；保留其他未提交改动。
- 原始源码纳管为普通仓库文件，不新增 Git submodule 或外部嵌套 Git 仓库，避免 SwiftPM 消费时额外检出。
- 原样快照与团队补丁分开：原始快照放 `apple/ThirdParty/`，编译所需派生源码放平台模块的 `Upstream/`，记录文件映射与补丁。首次审查后若无需改上游，优先直接编译纳管源码，避免重复拷贝。
- 保留 MIT LICENSE、版权、上游 URL、tag/commit、导入日期和本地修改说明。禁止将第三方代码改头后标为完全自研。
- 平台不支持、未知状态、查询失败、受限和用户拒绝不能合并为一个 Bool。
- 本地网络没有通用授权查询/显式申请 API；完整磁盘访问不得以路径探测结果宣称确定授权。
- Info.plist 用途声明、entitlements、应用签名和系统批准由宿主配置，库提供清单与诊断，不自动修改宿主权限。
- 仅在真实入口触发授权；不得启动时批量索取全部权限。取消当前等待不代表撤回系统授权或关闭系统弹框。
- 不泄露上游类型到团队公开 API，不强制基础权限逻辑依赖 DesignKit。

## Review Focus

- 首次系统授权尚未选择：不得误报永久拒绝、取消触发弹框的连接或重复弹窗。
- 请求中重复点击、页面关闭、前后台切换：不得重复恢复 continuation 或执行过期业务回调。
- 照片 limited、定位精度、通知 provisional 等：保留原有授权范围，不能都压成 authorized。
- macOS 沙盒与非沙盒、签名差异：未知就是未知，设置页打开成功不代表已授权。
- 文件 scope 只覆盖所选资源：异步读写全程有效、结束释放，持久授权仅由有效 bookmark 恢复。

## 拟定文件与接口

先在任务 1 核对现有模块名称，命名冲突必须在实施前修订本文。

| 路径 | 职责 |
|---|---|
| `apple/ThirdParty/PermissionsKit/`、`apple/ThirdParty/PermissionFlow/` | 经审查的上游源码、许可证与来源记录 |
| `apple/Sources/Shared/PermissionCore/` | 自有状态、可用能力描述、平台适配协议；不导入平台 UI |
| `apple/Sources/iOS/PermissionIOS/` | iOS 权限适配和应用设置入口 |
| `apple/Sources/macOS/PermissionMac/` | Mac 权限状态、设置入口、PermissionFlow 引导 |
| `apple/Tests/PermissionCoreTests/`、`apple/Tests/PermissionIOSTests/`、`apple/Tests/PermissionMacTests/` | 模拟权限提供者测试、平台实现测试 |
| `apple/Docs/Permissions.md`、`apple/Docs/Permissions-Upstream-Audit.md` | 接入文档、能力矩阵、上游审查及维护策略 |
| `Package.swift`、`apple/Tests/TEST_CASES.md` | 可选产品导出、真实用例同步 |

公开产品拟为 `PermissionCore`、`PermissionIOS`、`PermissionMac`。基础操作为状态查询、用户触发请求、打开设置及显式刷新；请求结果必须保留权限专有信息。具体 Swift 签名在源码审查后的 API 规格中锁定，避免当前未读实现就编造统一接口。

## Task 1：拉取、锁定、审查上游（准入关口）

- [ ] 查询两仓稳定 release、tag 和 commit；使用 git 拉取到临时审查目录，不运行上游安装脚本或构建插件。
- [ ] 核查许可证、传递依赖、资源、网络请求、自动更新、外部命令、私有 API、动态加载和凭据访问；记录实际发现，不能以 README 替代审查。
- [ ] 逐项核查权限语义、API availability、主线程与 Swift 6 并发、取消、请求去重、回调次数、内存及窗口生命周期、设置跳转失败路径。
- [ ] 特别审查 Full Disk Access 的探测依据、沙盒限制，以及是否存在误判成功；权限不足不能靠提权或改 TCC 数据库解决。
- [ ] 使用 `xcrun swift --version`、`xcodebuild -version` 核对本机，核对既有 CI；选定具体基线，记录 SHA 与发布年龄。工具链变更不得静默带入其他模块。
- [ ] 写入 `apple/Docs/Permissions-Upstream-Audit.md`：问题分级、复现、修复方案、可采用模块与不可采用部分；有阻断项先修并复测，无法修复则明确暂停对应能力，不声称“没有问题”。
- [ ] 按能力决定纳管清单和 target 依赖，保留完整来源及版权。验证没有嵌套 `.git`、本机路径、未授权下载或公开包缺失文件。

验收：源码版本可复现、许可清楚、编译条件明确、阻断问题均有结论，再进入公开 API 实现。

## Task 2：锁定接口并实现 iOS 权限闭环

- [ ] 基于任务 1 的能力矩阵补齐 `apple/Docs/Permissions.md` 的确切 API、每种权限返回值及平台限制，保持上游能力可访问，不擅自缩减用户所需范围。
- [ ] 先写失败测试：未决定到允许、拒绝后不再自动请求、受限与有限授权保真、重复请求去重、请求取消、回到前台显式刷新、平台不支持。
- [ ] 实现 PermissionCore 和 PermissionIOS，按需链接能力模块，避免消费者为相机授权被迫链接 HealthKit 等无关框架。
- [ ] 提供简洁的 SwiftUI 拒绝说明/设置入口组合，标题、用途说明和业务完成动作由宿主传入；使用现有 DesignKit 能力，不复制业务页面。
- [ ] 运行核心单元测试与 iOS Simulator 测试；同步 `apple/Tests/TEST_CASES.md`。验证消费者仅引入单项产品时也可编译。

验收：iOS 示例从用户操作到系统申请、拒绝提示、设置返回走通；保留平台权限专有结果。

## Task 3：实现 macOS 权限和设置引导闭环

- [ ] 先写失败测试：设置跳转被拒、未知状态、沙盒下不可确认的完整磁盘访问、重复展示引导、窗口关闭释放监听、返回设置只刷新一次。
- [ ] 实现 PermissionMac，复用经审查的 PermissionFlow 与 SystemSettingsKit；保留系统 API 申请和手动设置两类入口的差异。
- [ ] 引导窗口绑定调用窗口生命周期；支持取消、键盘、VoiceOver、中英文；不强迫宿主采用固定 onboarding 流程。
- [ ] 为上游问题增加最小回归用例，记录补丁，不顺带重写整套上游 UI。
- [ ] 运行 macOS 单元测试，在有签名的沙盒示例中验证真实授权；非沙盒仅作差异验证，不作为沙盒验收替代。

验收：macOS 示例可申请或引导支持的权限；打不开设置、无法确认授权时给出真实结果。

## Task 4：补齐 ADBox 所需本地网络与文件访问

- [ ] 先核对 ADBox 的 TCPProbe、权限恢复和文件 scope 调用链；复用已有实现，不另造假的权限查询接口。
- [ ] 为网络等待提供目标 host/port、超时与取消边界；测试首次授权等待、明确拒绝、ECONNREFUSED、无路由、取消与重复恢复。权限可通不等于业务端口开放。
- [ ] 文件选择继续使用原生面板；提取同步/异步 security scope 生命周期辅助，验证抛错与取消也释放；普通容器 URL 不应仅因 startAccessing 返回 false 被直接判为拒绝。
- [ ] 仅在真实跨启动复用需求存在时加入 bookmark 存储；否则保留临时访问并在文档写清限制。
- [ ] 基础库通过后，列出并迁移 ADBox 的两端权限入口；保留 ADBox 设备选择、重连归属和产品文案，不混入通用库。

验收：ADBox 首次允许后能继续连接，拒绝后不循环重连；选中文件可完成实际读写，取消和失败无 scope 泄漏。

## Task 5：文档、CI 与交付检查

- [ ] 补齐每个支持能力的 Info.plist、entitlement、系统最低版本、沙盒限制、首次/拒绝/受限/恢复验收表；不存在的通用 API 明确写为不支持。
- [ ] 更新团队 AppleAppKit Skill 的权限接入说明，跟随实际公开接口；示例仅请求演示能力，不一次性触发全部授权。
- [ ] 扩展现有 GitHub Actions 进行 macOS 与 iOS 编译/测试；真实隐私弹框保留有签名设备/桌面人工验收项，不以模拟返回值替代。
- [ ] 分别核对 SwiftPM 与 Xcode 消费依赖图，确认锁文件没有本机镜像污染；检查第三方许可证和资源随包可用。
- [ ] 汇总实际通过项、未测试能力、已知限制和上游补丁；提交仅含本任务文件。发布和业务仓推送另按用户指令执行。

## 维护策略

上游更新采用人工比对固定 SHA；每次升级先重放补丁和权限矩阵回归，再更新来源记录。团队接口遵循现有 SwiftPM 版本策略，第三方类型不对外暴露。不上线自动下载/替换源码能力。

## 执行顺序与完成标准

按任务 1 → 2 → 3 → 4 → 5 顺序执行。源码审查是准入步骤，不是“零缺陷保证”。完成须同时具备：可复现来源、两端可消费产品、必要测试、签名宿主真实权限流程证据及文档；无法取得实机/系统验收证据时明确标记未验收，不标记整项完成。

## 2026-11-17 实施记录

- 按用户后续指令，工作区已从 ios 改名 apple；SwiftPM、脚本、CI、模板和活动文档引用同步，历史发布记录保留当时目录语义。
- 任务 1 的固定版本源码、MIT 声明、补丁与风险审查已落盘；任务 2/3 的核心、16 个按需 iOS 能力、Mac 适配和独立说明 UI 已实现，共 20 个权限产品。
- 任务 4 的通用本地网络与文件访问机制已实现；ADBox 业务迁移需包含新产品的正式 tag 可消费后再做，本轮不自动发布或更换 ADBox 锁定依赖。
- 任务 5 的文档、双端宿主示例、测试清单、CI 编译目标已更新；远端 CI 和真实签名/隐私弹框/VoiceOver 未验收。
- Ruling: 通知、日历、提醒、定位、Health、生物识别不机械复用不准确的通用上游状态；采用原生精确接口并保留上游完整快照，代价是这些适配由团队自行维护。
- Ruling: 不新增第二份编译源码副本；直接编译 ThirdParty 中列出的纳管文件，补丁写入 DWY-UPSTREAM.md，避免源码与派生副本漂移。
- Ruling: 不提高部署版本或更改全局 Xcode 选择。上游包清单不参与根包编译，本机以 Swift 6.4.2 验证；现有 CI 工具链的实际结果须由远端运行确认。
- Ruling: 本机既有 GRDB 镜像使根 Xcode 解析失败；Xcode 权限验证使用从实际清单筛选的隔离依赖图，根 SwiftPM 验证单独执行，不修改用户镜像。
- 一次独立审查提出的通知升级、定位升级等待、旧引导残留、页面任务生命周期、历史 Changelog 误改均已修复。权限回归在 macOS 与 iOS 18.6 各 27 项通过；记录与限制见 apple/Docs/Permissions-Upstream-Audit.md。
