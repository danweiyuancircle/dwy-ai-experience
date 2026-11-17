#if os(macOS)
import AppKit
import AuthCore
import AuthGoogleMac
import XCTest

final class GoogleSignInProviderTests: XCTestCase {
    @MainActor
    func testConfigurationRejectsInvalidIDsAndProviderRequiresPresentingWindow() async throws {
        XCTAssertThrowsError(try MacGoogleSignInConfiguration(clientID: "", serverClientID: "server.apps.googleusercontent.com"))
        let config = try MacGoogleSignInConfiguration(clientID: "mac.apps.googleusercontent.com", serverClientID: "server.apps.googleusercontent.com")
        let provider = MacGoogleSignInProvider(configuration: config, presentingWindow: { nil })
        XCTAssertFalse(provider.handleURL(URL(string: "contextkit://settings")!))
        do {
            _ = try await provider.signIn()
            XCTFail("没有窗口不能发起浏览器认证")
        } catch AuthError.invalidConfiguration {} catch { XCTFail("unexpected error") }
    }
}
#endif
