import XCTest
@testable import AuthCore

/// 第三方新增入口不能绕过既有会话安装和迟到响应撤销规则。
@MainActor
final class ExternalSessionTests: XCTestCase {
    func testExternalSessionUsesReturnedIdentityAndPersistsRefreshToken() async throws {
        let backend = ExternalBackend()
        let tokens = MemoryTokens()
        let store = AuthSessionStore(backend: backend, tokenStore: tokens, deviceID: UUID())
        let operation = Task { try await store.signIn(provider: "apple", credential: "signed-credential") }
        while backend.pending == nil { await Task.yield() }
        backend.pending?.resume(returning: backend.response)
        try await operation.value
        XCTAssertEqual(store.session?.user.id, backend.response.user.id)
        XCTAssertEqual(tokens.token, "refresh")
    }

    func testLateExternalSessionIsRevokedAfterCancellation() async throws {
        let backend = ExternalBackend()
        let tokens = MemoryTokens()
        let store = AuthSessionStore(backend: backend, tokenStore: tokens, deviceID: UUID())
        let operation = Task { try await store.signIn(provider: "apple", credential: "signed-credential") }
        while backend.pending == nil { await Task.yield() }
        store.cancelPendingAuthentication()
        backend.pending?.resume(returning: backend.response)
        do { try await operation.value; XCTFail("Expected stale response") }
        catch AuthError.superseded {}
        XCTAssertNil(store.session)
        XCTAssertNil(tokens.token)
        XCTAssertEqual(backend.revoked, ["access"])
    }
}

@MainActor
private final class ExternalBackend: ExternalAuthBackend {
    let response = AuthTokenResponse(accessToken: "access", refreshToken: "refresh", expiresIn: 900, user: AuthUser(id: UUID(), email: nil, displayName: nil))
    var pending: CheckedContinuation<AuthTokenResponse, any Error>?
    var revoked: [String] = []
    func authenticate(provider: String, credential: String, deviceID: UUID) async throws -> AuthTokenResponse {
        try await withCheckedThrowingContinuation { pending = $0 }
    }
    func authenticate(googleIDToken: String, deviceID: UUID) async throws -> AuthTokenResponse { throw AuthError.invalidConfiguration }
    func refresh(refreshToken: String) async throws -> AuthTokenResponse { throw AuthError.invalidConfiguration }
    func logout(accessToken: String) async throws { revoked.append(accessToken) }
}

private final class MemoryTokens: RefreshTokenStoring {
    var token: String?
    func load() throws -> String? { token }
    func save(_ token: String) throws { self.token = token }
    func delete() throws { token = nil }
}
