import Foundation
import XCTest
@testable import SyncCore

/// 两个无关模型共享同一个引擎，防止框架隐式绑定 ADBox 字段。
final class SyncUsageTests: XCTestCase, @unchecked Sendable {
    private struct ShoppingItem: Codable, Sendable, Equatable { let name: String; let quantity: Int }
    private struct Bookmark: Codable, Sendable, Equatable { let url: String; let isRead: Bool }

    func testDifferentSchemasRoundTripWithoutCrossKindLeakage() async throws {
        let shopping = SyncSchema<ShoppingItem>(kind: "shopping_item", maxPayloadBytes: 256) { value in
            guard (1...99).contains(value.quantity), (1...40).contains(value.name.count) else {
                throw SyncError.invalidPayload("invalid item")
            }
        }
        let bookmarks = SyncSchema<Bookmark>(kind: "bookmark", maxPayloadBytes: 512) { value in
            guard value.url.utf8.count <= 256, URL(string: value.url)?.scheme == "https" else {
                throw SyncError.invalidPayload("invalid bookmark")
            }
        }
        let store = try SyncStore(
            directory: FileManager.default.temporaryDirectory.appendingPathComponent(UUID().uuidString),
            scope: SyncScope(backendURL: URL(string: "https://example.com/demo")!, appID: "demo", userID: nil),
            schemas: [shopping.erased, bookmarks.erased]
        )
        try await store.save(SyncDocument(id: UUID(), payload: ShoppingItem(name: "牛奶", quantity: 2)), using: shopping)
        try await store.save(SyncDocument(id: UUID(), payload: Bookmark(url: "https://example.com/article", isRead: false)), using: bookmarks)
        let items = try await store.documents(using: shopping, limit: 10, offset: 0)
        let links = try await store.documents(using: bookmarks, limit: 10, offset: 0)
        XCTAssertEqual(items.map(\.payload), [ShoppingItem(name: "牛奶", quantity: 2)])
        XCTAssertEqual(links.map(\.payload), [Bookmark(url: "https://example.com/article", isRead: false)])
    }
}
