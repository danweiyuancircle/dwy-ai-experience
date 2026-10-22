# 通用文档示例

以下完整 Swift 示例展示两个不同模型共用同一套本地 Store。服务器同步前，应在对应应用后端注册相同 kind 和字段；示例不连接现有 ADBox 服务端。

```swift
import Foundation
import SyncCore

/// 购物项只保存业务字段，UUID 与同步元数据由框架独立管理。
struct ShoppingItem: Codable, Sendable {
    let name: String
    let quantity: Int
}

/// 阅读书签与购物项不共享字段，但复用相同的事务与同步基础设施。
struct Bookmark: Codable, Sendable {
    let url: String
    let isRead: Bool
}

/// directory 由宿主提供 Application Support 下的持久目录，不能使用 Caches。
func localExample(directory: URL) async throws {
    let shopping = SyncSchema<ShoppingItem>(kind: "shopping_item", maxPayloadBytes: 256) { item in
        guard (1...40).contains(item.name.count), (1...99).contains(item.quantity) else {
            throw SyncError.invalidPayload("商品名称须为 1...40 字符，数量须为 1...99")
        }
    }
    let bookmarks = SyncSchema<Bookmark>(kind: "bookmark", maxPayloadBytes: 512) { item in
        guard item.url.utf8.count <= 256, URL(string: item.url)?.scheme == "https" else {
            throw SyncError.invalidPayload("书签须为不超过 256 字节的 HTTPS URL")
        }
    }
    let store = try SyncStore(
        directory: directory,
        scope: SyncScope(backendURL: URL(string: "https://example.com/demo")!, appID: "demo", userID: nil),
        schemas: [shopping.erased, bookmarks.erased]
    )
    try await store.save(SyncDocument(id: UUID(), payload: ShoppingItem(name: "牛奶", quantity: 2)), using: shopping)
    try await store.save(SyncDocument(id: UUID(), payload: Bookmark(url: "https://example.com/article", isRead: false)), using: bookmarks)
    let items = try await store.documents(using: shopping, limit: 20, offset: 0)
    let links = try await store.documents(using: bookmarks, limit: 20, offset: 0)
    print("购物项 \(items.count)，书签 \(links.count)")
}

/// store 必须是当前已认证用户对应的库；传输目标直接取同一 scope，避免环境错配。
func makeCoordinator(
    store: SyncStore,
    identityProvider: @escaping @Sendable (Bool) async throws -> SyncIdentity
) throws -> SyncCoordinator {
    let transport = try AppCloudSyncTransport(scope: store.scope, session: .shared, maxResponseBytes: 1_048_576)
    return SyncCoordinator(
        store: store,
        transport: transport,
        identityProvider: identityProvider,
        retryPolicy: try SyncRetryPolicy(maximumAttempts: 3, initialDelay: 1, maximumDelay: 30)
    )
}
```

宿主通过 `await coordinator.start()` 开启自动触发，通过 `try await coordinator.synchronize()` 手动刷新，通过 `await coordinator.pause()` 停止并卸载旧账号。完整生命周期与冲突处理见 `ios/Docs/SYNC_CORE.md`。
