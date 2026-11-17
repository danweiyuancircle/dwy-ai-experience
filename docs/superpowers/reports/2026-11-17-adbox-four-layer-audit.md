# ADBox 四层架构对齐审计

日期：2026-11-17。结论：当前目录与清单已具备双平台分包骨架，可按统一四层规范映射；本次只读审计，不代表全部内部实现或运行验收通过，不修改 ADBox。

## 范围与证据

核对 ADBox 当前 HEAD `8c7ae80281fd2b93c76f2e8e6cc8fbf334791397` 下的四份 Package.swift、两端 project.yml 的 sources / products、项目边界约定与 UI 目录。工作树可能另有未提交变更；结论以本次读取的实际文件为准，不把提交号视为所有文件均无差异。

| 入口（相对 ADBox 仓库根） | 已核实职责 | 四层映射 |
| --- | --- | --- |
| ios/App、macos/App | 各端独立入口、应用装配 | ① App |
| ios/Features、macos/Features | 各端功能页面 | ② Features |
| ios/UI/IOSUI、macos/UI/MacUI、macos/UI/Chrome | 平台 UI 产品与应用 UI | ②业务 UI；通用基础 UI 仍直接使用 AppleAppKit |
| packages/ADBoxUI | DesignKit、ADBoxUI 产品；按平台依赖 DesignKitIOS / DesignKitMac | 产品品牌与业务组合归②，通用能力仍归④ |
| packages/ADBoxCore | BizFoundation、ADBoxCloud、ClientLog products | ③产品共享业务；ClientLog 的通用性需按实现判断，不仅凭名字升层 |
| ios/Platform/IOSPlatform | iOS 专属适配，依赖 BizFoundation | ③平台业务适配 |
| macos/Platform/MacFoundation | macOS 专属适配，依赖 BizFoundation | ③平台业务适配 |
| 远端 dwy-ai-experience.git 产品 | CoreKit、L10nKit、DesignCore、DesignKitIOS / Mac、认证等 | ④ Foundation |

四份清单均读取到同一基础库精确版本 0.8.0-beta.6。本报告只记录该消费版本，不建议顺带升级到新模板默认版本，也不将基础库当前工作树的全部新 API 视为该 tag 已提供。

## 可直接保留

- 保留 ADBoxCore 与 ADBoxUI 两个已有共享包，不另外创建重复核心或 AppShared。
- 保留 IOSPlatform、MacFoundation 等稳定名称及平台隔离；平台包不新增第五层。
- 保留 ios/UI、macos/UI 的目录名，以职责视为功能层业务 UI；无需为改名搬到 BusinessUI 后才算合规。
- 两端工程通过 package products 引用共享业务和 UI。读取的 macOS sources 指向本端 App、Features、UI/Chrome 与资源，没有点名编译 ios 壳源码；完整有效 sources 仍应由原生工具和现有边界回归确认。

## 后续对齐顺序

1. **清单与 sources 检查**：检查两端实际生成工程、传递依赖与锁文件；确认无另一端源码、共享包重复编译或漏收录。
2. **UI 调用审查**：逐项检查 DesignKit、IOSUI、MacUI 的公开组件与调用方。满足需求的 AppleAppKit 组件直接使用；仅相同 API 的代理作为删除候选；确有品牌、业务状态或交互组合的组件保留。不凭 manifest 就认定全部是重复包装。
3. **业务与生命周期审查**：确认共享 BizFoundation 不依赖 UI、应用壳或具体平台实现；App 持有各端会话、路由、任务和资源释放，按协议注入平台能力。迁移组件不转移权限、购买或持久化所有权。
4. **分批迁移与回归**：按一组真实调用闭环实施，先记录现有结果，再跑受影响包、App 与设备交互；保留公开产品、文件存储路径、偏好 key、账号及同步语义。

## 限制

本轮未执行 ADBox 全量调用链审计、编译、单测、模拟器/真实设备交互或视觉验收；未修改 ADBox 的代码、目录、依赖、数据与项目规则。上述候选是后续审查边界，不是已确认缺陷，也不视为迁移完成。
