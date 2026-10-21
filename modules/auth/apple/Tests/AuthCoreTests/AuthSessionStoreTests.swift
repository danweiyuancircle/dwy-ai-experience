import XCTest
@testable import AuthCore

/// 用后端替身验证异步顺序，避免登录/刷新晚到时复活已退出会话。
@MainActor
final class AuthSessionStoreTests: XCTestCase {
    func testLoginUsesBackendIdentityAndOnlyPersistsRefreshToken() async throws {
        let backend = BackendStub()
        let tokens = TokenStoreStub()
        let store = AuthSessionStore(backend: backend, provider: ProviderStub(), tokenStore: tokens, deviceID: UUID())
        try await store.signIn()
        XCTAssertEqual(store.session?.user.id, backend.response.user.id)
        XCTAssertEqual(store.session?.accessToken, "access")
        XCTAssertEqual(tokens.token, "refresh")
    }

    func testRestoreRefreshesAndRotatesPersistedToken() async throws {
        let backend = BackendStub()
        let tokens = TokenStoreStub()
        tokens.token = "old"
        let store = AuthSessionStore(backend: backend, provider: ProviderStub(), tokenStore: tokens, deviceID: UUID())
        try await store.restore()
        XCTAssertEqual(backend.receivedRefreshTokens, ["old"])
        XCTAssertEqual(tokens.token, "refresh")
    }

    func testLogoutClearsLocalStateWhenNetworkFails() async throws {
        let backend = BackendStub()
        let tokens = TokenStoreStub()
        let provider = ProviderStub()
        let store = AuthSessionStore(backend: backend, provider: provider, tokenStore: tokens, deviceID: UUID())
        try await store.signIn()
        backend.logoutFails = true
        do { try await store.signOut(); XCTFail("Expected network failure") } catch {}
        XCTAssertNil(store.session)
        XCTAssertNil(tokens.token)
        XCTAssertEqual(backend.logoutTokens, [backend.response.accessToken])
        XCTAssertTrue(provider.didSignOut)
    }

    func testLogoutInvalidatesLateLogin() async throws {
        let backend = BackendStub()
        backend.pauseLogin = true
        let tokens = TokenStoreStub()
        let store = AuthSessionStore(backend: backend, provider: ProviderStub(), tokenStore: tokens, deviceID: UUID())
        let login = Task { try await store.signIn() }
        while backend.loginContinuation == nil { await Task.yield() }
        try await store.signOut()
        backend.loginContinuation?.resume(returning: backend.response)
        do { try await login.value; XCTFail("Expected superseded operation") } catch {}
        XCTAssertNil(store.session)
        XCTAssertNil(tokens.token)
        XCTAssertEqual(backend.logoutTokens, [backend.response.accessToken])
    }

    func testConcurrentRefreshIsSingleFlight() async throws {
        let backend = BackendStub()
        let tokens = TokenStoreStub()
        tokens.token = "old"
        backend.pauseRefresh = true
        let store = AuthSessionStore(backend: backend, provider: ProviderStub(), tokenStore: tokens, deviceID: UUID())
        let first = Task { try await store.refresh() }
        while backend.refreshContinuation == nil { await Task.yield() }
        let second = Task { try await store.refresh() }
        await Task.yield()
        backend.refreshContinuation?.resume(returning: backend.response)
        try await first.value
        try await second.value
        XCTAssertEqual(backend.receivedRefreshTokens, ["old"])
    }

    func testLogoutInvalidatesLateRefresh() async throws {
        let backend = BackendStub()
        let tokens = TokenStoreStub()
        tokens.token = "old"
        backend.pauseRefresh = true
        let store = AuthSessionStore(backend: backend, provider: ProviderStub(), tokenStore: tokens, deviceID: UUID())
        let refresh = Task { try await store.refresh() }
        while backend.refreshContinuation == nil { await Task.yield() }
        try await store.signOut()
        backend.refreshContinuation?.resume(returning: backend.response)
        do { try await refresh.value; XCTFail("Expected superseded operation") } catch {}
        XCTAssertNil(store.session)
        XCTAssertNil(tokens.token)
        XCTAssertEqual(backend.logoutTokens, [backend.response.accessToken])
    }

    func testLogoutRevokesRotatedTokenWhenOldAccessAlreadyInvalid() async throws {
        let backend = BackendStub()
        let tokens = TokenStoreStub()
        let store = AuthSessionStore(backend: backend, provider: ProviderStub(), tokenStore: tokens, deviceID: UUID())
        try await store.signIn()
        backend.response = AuthTokenResponse(accessToken: "rotated-access", refreshToken: "rotated-refresh", expiresIn: 900, user: backend.response.user)
        backend.pauseRefresh = true
        backend.logoutRejectedToken = "access"
        let refresh = Task { try await store.refresh() }
        while backend.refreshContinuation == nil { await Task.yield() }
        do { try await store.signOut(); XCTFail("Old token must be rejected") } catch {}
        backend.refreshContinuation?.resume(returning: backend.response)
        do { try await refresh.value; XCTFail("Expected superseded operation") } catch {}
        XCTAssertEqual(backend.logoutTokens, ["access", "rotated-access"])
        XCTAssertNil(store.session)
        XCTAssertNil(tokens.token)
    }

    func testKeychainDeleteFailureStillAttemptsServerRevocation() async throws {
        let backend = BackendStub()
        let tokens = TokenStoreStub()
        let store = AuthSessionStore(backend: backend, provider: ProviderStub(), tokenStore: tokens, deviceID: UUID())
        try await store.signIn()
        tokens.deleteFails = true
        do { try await store.signOut(); XCTFail("Expected storage failure") } catch {}
        XCTAssertEqual(backend.logoutTokens, ["access"])
        XCTAssertNil(store.session)
    }

    func testKeychainSaveFailureRevokesReturnedSession() async throws {
        let backend = BackendStub()
        let tokens = TokenStoreStub()
        tokens.saveFails = true
        let store = AuthSessionStore(backend: backend, provider: ProviderStub(), tokenStore: tokens, deviceID: UUID())
        do { try await store.signIn(); XCTFail("Expected storage failure") } catch {}
        XCTAssertEqual(backend.logoutTokens, ["access"])
        XCTAssertNil(store.session)
    }

    func testPermanentlyInvalidRefreshClearsLocalSession() async throws {
        let backend = BackendStub()
        let tokens = TokenStoreStub()
        let store = AuthSessionStore(backend: backend, provider: ProviderStub(), tokenStore: tokens, deviceID: UUID())
        try await store.signIn()
        backend.refreshError = AuthError.server(code: "REFRESH_TOKEN_INVALID", message: "expired")
        do { try await store.refresh(); XCTFail("Expected invalid refresh") } catch {}
        XCTAssertNil(store.session)
        XCTAssertNil(tokens.token)
    }
}

/// 内存替身仅供状态机测试，不接触系统 Keychain。
@MainActor
private final class TokenStoreStub: RefreshTokenStoring {
    var token: String?
    var saveFails = false
    var deleteFails = false
    func load() throws -> String? { token }
    func save(_ token: String) throws {
        if saveFails { throw AuthError.keychain(-1) }
        self.token = token
    }
    func delete() throws {
        if deleteFails { throw AuthError.keychain(-1) }
        token = nil
    }
}

/// SDK 替身只产出 ID token，用户身份必须来自后端。
@MainActor
private final class ProviderStub: GoogleIDTokenProviding {
    var didSignOut = false
    func signIn() async throws -> String { "google-id-token" }
    func signOut() { didSignOut = true }
}

/// 可暂停网络边界以重现请求迟到。
@MainActor
private final class BackendStub: AuthBackend {
    var response = AuthTokenResponse(accessToken: "access", refreshToken: "refresh", expiresIn: 900, user: AuthUser(id: UUID(), email: "user@example.com", displayName: "User"))
    var receivedRefreshTokens: [String] = []
    var logoutFails = false
    var pauseLogin = false
    var pauseRefresh = false
    var refreshError: Error?
    var logoutTokens: [String] = []
    var logoutRejectedToken: String?
    var loginContinuation: CheckedContinuation<AuthTokenResponse, Error>?
    var refreshContinuation: CheckedContinuation<AuthTokenResponse, Error>?
    func authenticate(googleIDToken: String, deviceID: UUID) async throws -> AuthTokenResponse {
        if pauseLogin { return try await withCheckedThrowingContinuation { loginContinuation = $0 } }
        return response
    }
    func refresh(refreshToken: String) async throws -> AuthTokenResponse {
        receivedRefreshTokens.append(refreshToken)
        if let refreshError { throw refreshError }
        if pauseRefresh { return try await withCheckedThrowingContinuation { refreshContinuation = $0 } }
        return response
    }
    func logout(accessToken: String) async throws {
        logoutTokens.append(accessToken)
        if accessToken == logoutRejectedToken { throw AuthError.server(code: "ACCESS_TOKEN_INVALID", message: "rotated") }
        if logoutFails { throw URLError(.notConnectedToInternet) }
    }
}
