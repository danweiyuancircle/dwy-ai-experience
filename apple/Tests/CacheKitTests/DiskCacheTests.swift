import XCTest
@testable import CacheKit

final class DiskCacheTests: XCTestCase {
    private var tempDir: URL!
    private var cache: DiskCache!

    override func setUpWithError() throws {
        try super.setUpWithError()
        tempDir = FileManager.default.temporaryDirectory
            .appendingPathComponent("CacheKitTests-\(UUID().uuidString)", isDirectory: true)
        try FileManager.default.createDirectory(at: tempDir, withIntermediateDirectories: true)
        cache = DiskCache(root: tempDir)
    }

    override func tearDownWithError() throws {
        try? FileManager.default.removeItem(at: tempDir)
        cache = nil
        tempDir = nil
        try super.tearDownWithError()
    }

    func testSaveLoadCodable() throws {
        struct Item: Codable, Equatable { let name: String }
        try cache.save(Item(name: "a"), namespace: "n", key: "k", cacheKey: "dev1")
        let loaded = try cache.load(Item.self, namespace: "n", key: "k", cacheKey: "dev1")
        XCTAssertEqual(loaded, Item(name: "a"))
        XCTAssertTrue(cache.hasCache(cacheKey: "dev1"))
    }

    func testMissingReturnsNil() throws {
        let loaded = try cache.load(String.self, namespace: "n", key: "missing", cacheKey: "dev1")
        XCTAssertNil(loaded)
    }

    func testClear() throws {
        try cache.saveData(Data([1, 2, 3]), namespace: "n", key: "k", cacheKey: "dev1")
        try cache.clear(cacheKey: "dev1")
        XCTAssertFalse(cache.hasCache(cacheKey: "dev1"))
    }
}
