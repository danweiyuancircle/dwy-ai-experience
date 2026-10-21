# ③ BizFoundation（业务基础层）

对应 TVRemote 的 `Sources/BizFoundation`。

- 领域模型、状态机、解析、策略 — **纯逻辑**
- 可 `swift test`（`Tests/BizFoundationTests`）
- **禁止** `import SwiftUI` / UIKit

依赖 ④：`CoreKit` / `L10nKit` / `LogKit` / `CacheKit`（骨架 product）。

扩展示例：`Session/`、`Models/`、`Services/` 子目录。
