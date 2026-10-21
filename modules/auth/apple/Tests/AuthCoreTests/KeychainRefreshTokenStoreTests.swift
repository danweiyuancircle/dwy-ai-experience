import XCTest
@testable import AuthCore

/// 仅操作随机测试 namespace，不读取宿主应用或 SDK 凭据。
@MainActor
final class KeychainRefreshTokenStoreTests: XCTestCase {
    func testRoundTripRotationAndDelete() throws {
        let store = try KeychainRefreshTokenStore(namespace: "AuthCoreTests." + UUID().uuidString, backendURL: URL(string: "https://example.com/adbox")!)
        XCTAssertNil(try store.load())
        try store.save("first")
        XCTAssertEqual(try store.load(), "first")
        try store.save("rotated")
        XCTAssertEqual(try store.load(), "rotated")
        try store.delete()
        XCTAssertNil(try store.load())
    }

    func testApplicationsOnSameOriginHaveIndependentTokens() throws {
        let namespace = "AuthCoreTests." + UUID().uuidString
        let adbox = try KeychainRefreshTokenStore(namespace: namespace, backendURL: URL(string: "https://example.com/adbox")!)
        let rightflow = try KeychainRefreshTokenStore(namespace: namespace, backendURL: URL(string: "https://example.com/rightflow")!)
        try adbox.save("adbox-token")
        XCTAssertNil(try rightflow.load())
        try rightflow.save("rightflow-token")
        XCTAssertEqual(try adbox.load(), "adbox-token")
        try adbox.delete()
        try rightflow.delete()
    }

    func testDeviceIdentifierPersistsAndSeparatesApplications() throws {
        let defaults = UserDefaults(suiteName: "AuthCoreTests." + UUID().uuidString)!
        let first = try AuthDeviceIdentity.loadOrCreate(namespace: "adbox", defaults: defaults)
        XCTAssertEqual(try AuthDeviceIdentity.loadOrCreate(namespace: "adbox", defaults: defaults), first)
        XCTAssertNotEqual(try AuthDeviceIdentity.loadOrCreate(namespace: "rightflow", defaults: defaults), first)
        defaults.removeObject(forKey: "adbox.auth.device-id")
        defaults.removeObject(forKey: "rightflow.auth.device-id")
    }
}
