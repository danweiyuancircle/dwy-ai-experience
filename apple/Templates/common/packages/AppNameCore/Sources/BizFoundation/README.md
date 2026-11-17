# ③ BizFoundation（业务基础层）

本产品核心包的共享逻辑 target；iOS、macOS 引用同一份，不复制到平台壳。

- 领域模型、状态机、解析、策略 — **纯逻辑**
- 产品根执行 `swift test --package-path packages/__APP_NAME__Core`（测试位于 `packages/__APP_NAME__Core/Tests/BizFoundationTests`）
- **禁止** `import SwiftUI` / UIKit

业务 UI 放在本端 BusinessUI（②）并编入 App target；平台业务实现按需放本端 Platform（③），不放进共享逻辑 target。

依赖 ④：`CoreKit` / `L10nKit` / `LogKit` / `CacheKit`（骨架 product）。

扩展示例：`Session/`、`Models/`、`Services/` 子目录。
