import XCTest
@testable import AuthCore

/// 用后端替身验证异步顺序，避免登录/刷新晚到时复活已退出会话。
@MainActor
final class AuthSessionStoreTests: XCTestCase {
    func testAppleManagementProofUsesCurrentSessionAndServerNonce() async throws {
        let backend = BackendStub()
        let provider = AppleProviderStub()
        let store = AuthSessionStore(backend: backend, tokenStore: TokenStoreStub(), deviceID: UUID())
        try await store.signIn(email: "user@example.com", password: "password")
        let proof = try await store.prepareAppleReauthentication(provider: provider, purpose: .emailUpdate)
        XCTAssertEqual(backend.managementTokens, ["access"])
        XCTAssertEqual(provider.nonces, ["raw-nonce"])
        let fields = try XCTUnwrap(JSONSerialization.jsonObject(with: JSONEncoder().encode(proof)) as? [String: String])
        XCTAssertEqual(fields["identifier"], "apple")
        XCTAssertEqual(store.session?.accessToken, "access")
    }

    func testAppleManagementChallengeCannotPresentAfterAccountLogout() async throws {
        let backend = BackendStub()
        let provider = AppleProviderStub()
        let store = AuthSessionStore(backend: backend, tokenStore: TokenStoreStub(), deviceID: UUID())
        try await store.signIn(email: "user@example.com", password: "password")
        backend.pauseAppleChallenge = true
        let task = Task { try await store.prepareAppleReauthentication(provider: provider, purpose: .emailUpdate) }
        while backend.appleChallengeContinuation == nil { await Task.yield() }
        try await store.signOut()
        backend.appleChallengeContinuation?.resume(returning: backend.appleChallenge)
        do { _ = try await task.value; XCTFail("Expected changed session rejection") }
        catch AuthError.superseded {}
        XCTAssertTrue(provider.nonces.isEmpty)
    }

    func testCancelledAppleManagementAuthorizationDoesNotReturnProof() async throws {
        let backend = BackendStub()
        let provider = AppleProviderStub()
        let store = AuthSessionStore(backend: backend, tokenStore: TokenStoreStub(), deviceID: UUID())
        try await store.signIn(email: "user@example.com", password: "password")
        provider.pause = true
        let task = Task { try await store.prepareAppleReauthentication(provider: provider, purpose: .unlink) }
        while provider.continuation == nil { await Task.yield() }
        task.cancel()
        provider.continuation?.resume(returning: provider.authorization)
        do { _ = try await task.value; XCTFail("Expected task cancellation") }
        catch is CancellationError {}
    }
    func testAppleSignInPassesRawNonceAndInstallsOnlyBackendRefreshToken() async throws {
        let backend = BackendStub()
        let tokens = TokenStoreStub()
        let provider = AppleProviderStub()
        let deviceID = UUID()
        let store = AuthSessionStore(backend: backend, tokenStore: tokens, deviceID: deviceID)
        try await store.signInWithApple(provider: provider)
        XCTAssertEqual(provider.nonces, ["raw-nonce"])
        XCTAssertEqual(backend.appleAuthorization?.identityToken, "apple-id-token")
        XCTAssertEqual(backend.appleAuthorization?.authorizationCode, "apple-code")
        XCTAssertEqual(backend.appleAuthorization?.displayName, "Untrusted Name")
        XCTAssertEqual(backend.appleChallengeID, "apple-challenge")
        XCTAssertEqual(backend.appleDeviceID, deviceID)
        XCTAssertEqual(store.session?.user, backend.response.user)
        XCTAssertEqual(tokens.token, "refresh")
        XCTAssertFalse(store.isSigningIn)
    }

    func testAppleCancellationAndDuplicateTapNeverExchangeAuthorization() async throws {
        let backend = BackendStub()
        let provider = AppleProviderStub()
        provider.pause = true
        let store = AuthSessionStore(backend: backend, tokenStore: TokenStoreStub(), deviceID: UUID())
        let login = Task { try await store.signInWithApple(provider: provider) }
        while provider.continuation == nil { await Task.yield() }
        try await store.signInWithApple(provider: provider)
        XCTAssertEqual(provider.nonces.count, 1)
        provider.continuation?.resume(throwing: CancellationError())
        do { try await login.value; XCTFail("Expected cancellation") } catch is CancellationError {}
        XCTAssertNil(store.session)
        XCTAssertNil(backend.appleAuthorization)
        XCTAssertFalse(store.isSigningIn)
    }

    func testCancelWhileAppleChallengeIsPendingDoesNotPresentNativeAuthorization() async throws {
        let backend = BackendStub()
        backend.pauseAppleChallenge = true
        let provider = AppleProviderStub()
        let store = AuthSessionStore(backend: backend, tokenStore: TokenStoreStub(), deviceID: UUID())
        let login = Task { try await store.signInWithApple(provider: provider) }
        while backend.appleChallengeContinuation == nil { await Task.yield() }
        store.cancelPendingAuthentication()
        backend.appleChallengeContinuation?.resume(returning: backend.appleChallenge)
        do { try await login.value; XCTFail("Expected superseded operation") } catch AuthError.superseded {}
        XCTAssertTrue(provider.nonces.isEmpty)
        XCTAssertNil(backend.appleAuthorization)
    }

    func testCancelPendingAppleAuthorizationRejectsLateNativeCallback() async throws {
        let backend = BackendStub()
        let provider = AppleProviderStub()
        provider.pause = true
        let store = AuthSessionStore(backend: backend, tokenStore: TokenStoreStub(), deviceID: UUID())
        let login = Task { try await store.signInWithApple(provider: provider) }
        while provider.continuation == nil { await Task.yield() }
        store.cancelPendingAuthentication()
        provider.continuation?.resume(returning: provider.authorization)
        do { try await login.value; XCTFail("Expected superseded operation") } catch AuthError.superseded {}
        XCTAssertNil(backend.appleAuthorization)
        XCTAssertNil(store.session)
    }

    func testAppleLateBackendSessionAfterLogoutIsRevoked() async throws {
        let backend = BackendStub()
        backend.pauseLogin = true
        let tokens = TokenStoreStub()
        let store = AuthSessionStore(backend: backend, tokenStore: tokens, deviceID: UUID())
        let login = Task { try await store.signInWithApple(provider: AppleProviderStub()) }
        while backend.loginContinuation == nil { await Task.yield() }
        try await store.signOut()
        backend.loginContinuation?.resume(returning: backend.response)
        do { try await login.value; XCTFail("Expected superseded operation") } catch AuthError.superseded {}
        XCTAssertNil(store.session)
        XCTAssertNil(tokens.token)
        XCTAssertEqual(backend.logoutTokens, ["access"])
    }

    func testAppleTaskCancellationRejectsLateBackendSession() async throws {
        let backend = BackendStub()
        backend.pauseLogin = true
        backend.logoutRejectsCancelledTask = true
        let tokens = TokenStoreStub()
        let store = AuthSessionStore(backend: backend, tokenStore: tokens, deviceID: UUID())
        let login = Task { try await store.signInWithApple(provider: AppleProviderStub()) }
        while backend.loginContinuation == nil { await Task.yield() }
        login.cancel()
        backend.loginContinuation?.resume(returning: backend.response)
        do { try await login.value; XCTFail("Expected task cancellation") } catch is CancellationError {}
        XCTAssertNil(store.session)
        XCTAssertNil(tokens.token)
        XCTAssertEqual(backend.logoutTokens, ["access"])
        XCTAssertFalse(store.isSigningIn)
    }

    func testAppleKeychainFailureRevokesSessionAndExistingBackendRemainsCompatible() async throws {
        let backend = BackendStub()
        let tokens = TokenStoreStub()
        tokens.saveFails = true
        let store = AuthSessionStore(backend: backend, tokenStore: tokens, deviceID: UUID())
        do { try await store.signInWithApple(provider: AppleProviderStub()); XCTFail("Expected keychain failure") }
        catch AuthError.keychain {}
        XCTAssertNil(store.session)
        XCTAssertNil(tokens.token)
        XCTAssertEqual(backend.logoutTokens, ["access"])
        let oldStore = AuthSessionStore(backend: GoogleOnlyBackend(), provider: ProviderStub(), tokenStore: TokenStoreStub(), deviceID: UUID())
        do { try await oldStore.signInWithApple(provider: AppleProviderStub()); XCTFail("Expected absent Apple capability") }
        catch AuthError.invalidConfiguration {}
        try await oldStore.signIn()
        XCTAssertNotNil(oldStore.session)
    }

    /// B 登录已开始时 A 会话尚在内存，管理入口不得携带 A token 发请求。
    func testManagementCallsStartedDuringOtherAccountLoginAreRejected() async throws {
        for action in ["list", "code", "bind", "unlink"] {
            let backend = BackendStub()
            let tokens = TokenStoreStub()
            let store = AuthSessionStore(backend: backend, tokenStore: tokens, deviceID: UUID())
            try await store.signIn(email: "a@example.com", password: "password")
            backend.pauseLogin = true
            let login = Task { try await store.signIn(email: "b@example.com", password: "password") }
            while backend.loginContinuation == nil { await Task.yield() }
            do {
                switch action {
                case "list": _ = try await store.listIdentities()
                case "code": _ = try await store.sendEmailUpdateCode(email: "updated@example.com", reauthentication: .email(identifier: "a@example.com", password: "password"))
                case "bind": try await store.bindExternal(provider: "google", credential: "id-token", reauthentication: .email(identifier: "a@example.com", password: "password"))
                default: try await store.unlinkIdentity(AuthLoginIdentity(kind: .email, value: "a@example.com"), reauthentication: .email(identifier: "a@example.com", password: "password"))
                }
                XCTFail("Management must reject pending B login: \(action)")
            } catch AuthError.superseded {}
            XCTAssertTrue(backend.managementTokens.isEmpty, action)
            backend.loginContinuation?.resume(returning: AuthTokenResponse(accessToken: "b-access", refreshToken: "b-refresh", expiresIn: 900, user: AuthUser(id: UUID(), email: "b@example.com", displayName: nil)))
            try await login.value
            XCTAssertEqual(store.session?.user.email, "b@example.com")
        }
    }

    /// 同一账号刷新替换会话后，旧会话的管理响应也不能继续返回页面。
    func testManagementResponseRejectsChangedSessionWithinSameGeneration() async throws {
        let backend = BackendStub()
        let tokens = TokenStoreStub()
        let store = AuthSessionStore(backend: backend, tokenStore: tokens, deviceID: UUID())
        try await store.signIn(email: "a@example.com", password: "password")
        backend.pauseManagement = true
        let listing = Task { try await store.listIdentities() }
        while backend.managementContinuation == nil { await Task.yield() }
        backend.response = AuthTokenResponse(accessToken: "rotated-access", refreshToken: "rotated-refresh", expiresIn: 900, user: backend.response.user)
        try await store.refresh()
        backend.managementContinuation?.resume(returning: [])
        do { _ = try await listing.value; XCTFail("Expected changed session rejection") }
        catch AuthError.superseded {}
        XCTAssertEqual(store.session?.accessToken, "rotated-access")
    }

    /// 轮换后的 refresh 仍只能由 SDK 安装，固定 userId。
    func testEmailUpdateInstallsRotatedSessionForSameUser() async throws {
        let backend = BackendStub()
        let tokens = TokenStoreStub()
        let store = AuthSessionStore(backend: backend, tokenStore: tokens, deviceID: UUID())
        try await store.signIn(email: "user@example.com", password: "password")
        let userID = backend.response.user.id
        backend.response = AuthTokenResponse(accessToken: "updated-access", refreshToken: "updated-refresh", expiresIn: 900, user: AuthUser(id: userID, email: "updated@example.com", displayName: nil))
        try await store.updateEmail(email: "updated@example.com", code: "012345", challengeID: "challenge", newPassword: nil)
        XCTAssertEqual(store.session?.user.id, userID)
        XCTAssertEqual(store.session?.user.email, "updated@example.com")
        XCTAssertEqual(tokens.token, "updated-refresh")
    }

    /// A 的邮箱响应迟到时必须撤销 A 的新会话，保留随后登录的 B。
    func testLateEmailUpdateCannotReplaceAnotherAccount() async throws {
        let backend = BackendStub()
        let tokens = TokenStoreStub()
        let store = AuthSessionStore(backend: backend, tokenStore: tokens, deviceID: UUID())
        try await store.signIn(email: "user@example.com", password: "password")
        let stale = backend.response
        backend.pauseUpdate = true
        let update = Task { try await store.updateEmail(email: "updated@example.com", code: "012345", challengeID: "challenge", newPassword: nil) }
        while backend.updateContinuation == nil { await Task.yield() }
        try await store.signOut()
        backend.response = AuthTokenResponse(accessToken: "b-access", refreshToken: "b-refresh", expiresIn: 900, user: AuthUser(id: UUID(), email: "b@example.com", displayName: nil))
        try await store.signIn(email: "b@example.com", password: "password")
        backend.updateContinuation?.resume(returning: stale)
        do { try await update.value; XCTFail("Expected stale response") } catch AuthError.superseded {}
        XCTAssertEqual(store.session?.user.id, backend.response.user.id)
        XCTAssertEqual(tokens.token, "b-refresh")
    }

    func testSuccessfulPasswordResetClearsLocalSessionWithoutLoggingOutRevokedToken() async throws {
        let backend = BackendStub()
        let tokens = TokenStoreStub()
        let provider = ProviderStub()
        let store = AuthSessionStore(backend: backend, provider: provider, tokenStore: tokens, deviceID: UUID())
        try await store.signIn(email: "user@example.com", password: "password")
        try await store.resetPassword(email: "user@example.com", password: "password1234567", code: "012345", challengeID: "challenge")
        XCTAssertNil(store.session)
        XCTAssertNil(tokens.token)
        XCTAssertFalse(store.isSigningIn)
        XCTAssertTrue(provider.didSignOut)
        XCTAssertTrue(backend.logoutTokens.isEmpty)
    }

    func testFailedPasswordResetPreservesLocalSession() async throws {
        let backend = BackendStub()
        let tokens = TokenStoreStub()
        let store = AuthSessionStore(backend: backend, tokenStore: tokens, deviceID: UUID())
        try await store.signIn(email: "user@example.com", password: "password")
        backend.resetError = AuthError.server(code: "EMAIL_CODE_INVALID", message: "invalid")
        do { try await store.resetPassword(email: "user@example.com", password: "password1234567", code: "012345", challengeID: "challenge"); XCTFail("Expected reset failure") }
        catch AuthError.server(let code, _) { XCTAssertEqual(code, "EMAIL_CODE_INVALID") }
        XCTAssertEqual(store.session?.accessToken, "access")
        XCTAssertEqual(tokens.token, "refresh")
        XCTAssertTrue(backend.logoutTokens.isEmpty)
    }

    func testSuccessfulResetReportsKeychainDeletionFailureAndClearsMemory() async throws {
        let backend = BackendStub()
        let tokens = TokenStoreStub()
        let store = AuthSessionStore(backend: backend, tokenStore: tokens, deviceID: UUID())
        try await store.signIn(email: "user@example.com", password: "password")
        tokens.deleteFails = true
        do { try await store.resetPassword(email: "user@example.com", password: "password1234567", code: "012345", challengeID: "challenge"); XCTFail("Expected storage failure") }
        catch AuthError.keychain {}
        XCTAssertNil(store.session)
        XCTAssertTrue(backend.logoutTokens.isEmpty)
    }

    func testPasswordResetInvalidatesLateRestoreAndAllowsSubsequentLogin() async throws {
        let backend = BackendStub()
        let stale = backend.response
        let tokens = TokenStoreStub()
        tokens.token = "old-refresh"
        backend.pauseRefresh = true
        let store = AuthSessionStore(backend: backend, tokenStore: tokens, deviceID: UUID())
        let restore = Task { try await store.restore() }
        while backend.refreshContinuation == nil { await Task.yield() }
        try await store.resetPassword(email: "user@example.com", password: "password1234567", code: "012345", challengeID: "challenge")
        backend.refreshContinuation?.resume(returning: stale)
        do { try await restore.value; XCTFail("Expected stale restore rejection") } catch AuthError.superseded {}
        XCTAssertNil(store.session)
        XCTAssertNil(tokens.token)
        backend.response = AuthTokenResponse(accessToken: "new-access", refreshToken: "new-refresh", expiresIn: 900, user: stale.user)
        try await store.signIn(email: "user@example.com", password: "password1234567")
        XCTAssertEqual(store.session?.accessToken, "new-access")
        XCTAssertEqual(tokens.token, "new-refresh")
        XCTAssertEqual(backend.logoutTokens, ["access"])
    }

    func testPasswordResetInvalidatesLateSignInWithoutReplacingSubsequentLogin() async throws {
        let backend = BackendStub()
        let stale = backend.response
        let tokens = TokenStoreStub()
        backend.pauseLogin = true
        let store = AuthSessionStore(backend: backend, tokenStore: tokens, deviceID: UUID())
        let login = Task { try await store.signIn(email: "user@example.com", password: "old-password") }
        while backend.loginContinuation == nil { await Task.yield() }
        try await store.resetPassword(email: "user@example.com", password: "password1234567", code: "012345", challengeID: "challenge")
        backend.pauseLogin = false
        backend.response = AuthTokenResponse(accessToken: "new-access", refreshToken: "new-refresh", expiresIn: 900, user: stale.user)
        try await store.signIn(email: "user@example.com", password: "password1234567")
        backend.loginContinuation?.resume(returning: stale)
        do { try await login.value; XCTFail("Expected stale login rejection") } catch AuthError.superseded {}
        XCTAssertEqual(store.session?.accessToken, "new-access")
        XCTAssertEqual(tokens.token, "new-refresh")
        XCTAssertEqual(backend.logoutTokens, ["access"])
    }

    func testLatePasswordResetDoesNotClearSubsequentLogin() async throws {
        let backend = BackendStub()
        let tokens = TokenStoreStub()
        backend.pauseReset = true
        let store = AuthSessionStore(backend: backend, tokenStore: tokens, deviceID: UUID())
        let reset = Task { try await store.resetPassword(email: "user@example.com", password: "password1234567", code: "012345", challengeID: "challenge") }
        while backend.resetContinuation == nil { await Task.yield() }
        try await store.signIn(email: "user@example.com", password: "password1234567")
        backend.resetContinuation?.resume()
        try await reset.value
        XCTAssertEqual(store.session?.accessToken, "access")
        XCTAssertEqual(tokens.token, "refresh")
        XCTAssertTrue(backend.logoutTokens.isEmpty)
    }

    func testGoogleOnlyBackendRemainsCompatibleAndRejectsEmailConfiguration() async throws {
        let store = AuthSessionStore(backend: GoogleOnlyBackend(), provider: ProviderStub(), tokenStore: TokenStoreStub(), deviceID: UUID())
        try await store.signIn()
        XCTAssertNotNil(store.session)
        do { try await store.signIn(email: "user@example.com", password: "password"); XCTFail("Missing email backend") }
        catch AuthError.invalidConfiguration {}
    }

    func testEmailRegistrationKeychainFailureRevokesReturnedSession() async throws {
        let backend = BackendStub()
        let tokens = TokenStoreStub()
        tokens.saveFails = true
        let store = AuthSessionStore(backend: backend, tokenStore: tokens, deviceID: UUID())
        do { try await store.register(email: "user@example.com", password: "password1234567", code: "012345", challengeID: "challenge"); XCTFail("Expected keychain failure") }
        catch let error as AuthRegistrationError {
            guard case AuthError.keychain = error.installationError else { return XCTFail("Expected original storage error") }
        }
        XCTAssertNil(store.session)
        XCTAssertNil(tokens.token)
        XCTAssertEqual(backend.logoutTokens, ["access"])
    }

    func testCancelPendingAuthenticationInvalidatesLateEmailLogin() async throws {
        let backend = BackendStub()
        let tokens = TokenStoreStub()
        let store = AuthSessionStore(backend: backend, tokenStore: tokens, deviceID: UUID())
        try await store.signIn(email: "user@example.com", password: "password")
        backend.pauseLogin = true
        let login = Task { try await store.signIn(email: "other@example.com", password: "password") }
        while backend.loginContinuation == nil { await Task.yield() }
        store.cancelPendingAuthentication()
        XCTAssertFalse(store.isSigningIn)
        XCTAssertEqual(store.session?.accessToken, "access")
        backend.loginContinuation?.resume(returning: backend.response)
        do { try await login.value; XCTFail("Expected superseded operation") } catch AuthError.superseded {}
        XCTAssertEqual(backend.logoutTokens, ["access"])
        XCTAssertEqual(tokens.token, "refresh")
    }
    func testEmailLoginAndRegistrationWorkWithoutGoogleAndInstallSession() async throws {
        let backend = BackendStub()
        let tokens = TokenStoreStub()
        let store = AuthSessionStore(backend: backend, tokenStore: tokens, deviceID: UUID())
        try await store.signIn(email: "user@example.com", password: "password")
        XCTAssertEqual(store.session?.accessToken, "access")
        XCTAssertEqual(tokens.token, "refresh")
        try await store.signOut()
        try await store.register(email: "user@example.com", password: "password", code: "012345", challengeID: "challenge")
        XCTAssertEqual(store.session?.user.id, backend.response.user.id)
        XCTAssertEqual(tokens.token, "refresh")
        do { try await store.signIn(); XCTFail("Missing Google provider") } catch AuthError.invalidConfiguration {}
    }

    func testEmailRegistrationLateCallbackIsRevokedAfterLogout() async throws {
        let backend = BackendStub()
        backend.pauseLogin = true
        let tokens = TokenStoreStub()
        let store = AuthSessionStore(backend: backend, tokenStore: tokens, deviceID: UUID())
        let registration = Task { try await store.register(email: "user@example.com", password: "password", code: "012345", challengeID: "challenge") }
        while backend.loginContinuation == nil { await Task.yield() }
        try await store.signOut()
        backend.loginContinuation?.resume(returning: backend.response)
        do { try await registration.value; XCTFail("Expected superseded operation") }
        catch let error as AuthRegistrationError {
            guard case AuthError.superseded = error.installationError else { return XCTFail("Expected original superseded error") }
        }
        XCTAssertNil(store.session)
        XCTAssertNil(tokens.token)
        XCTAssertEqual(backend.logoutTokens, ["access"])
    }

    func testRefreshIfNeededSkipsFreshAccessThenRefreshesWithinSixtySeconds() async throws {
        let backend = BackendStub()
        let tokens = TokenStoreStub()
        var now = Date(timeIntervalSince1970: 0)
        let store = AuthSessionStore(backend: backend, tokenStore: tokens, deviceID: UUID(), now: { now })
        try await store.signIn(email: "user@example.com", password: "password")
        now = Date(timeIntervalSince1970: 840)
        try await store.refreshIfNeeded()
        XCTAssertTrue(backend.receivedRefreshTokens.isEmpty)
        now = Date(timeIntervalSince1970: 841)
        try await store.refreshIfNeeded()
        XCTAssertEqual(backend.receivedRefreshTokens, ["refresh"])
    }

    func testRefreshIfNeededRestoresAndPreservesTokenOnTemporaryFailure() async throws {
        let backend = BackendStub()
        let tokens = TokenStoreStub()
        tokens.token = "persisted"
        let store = AuthSessionStore(backend: backend, tokenStore: tokens, deviceID: UUID())
        backend.refreshError = URLError(.notConnectedToInternet)
        do { try await store.refreshIfNeeded(); XCTFail("Expected temporary failure") } catch {}
        XCTAssertEqual(tokens.token, "persisted")
        XCTAssertNil(store.session)
        backend.refreshError = nil
        try await store.refreshIfNeeded()
        XCTAssertEqual(store.session?.accessToken, "access")
    }

    func testSendCodeAndResetDoNotInstallSession() async throws {
        let tokens = TokenStoreStub()
        let store = AuthSessionStore(backend: BackendStub(), tokenStore: tokens, deviceID: UUID())
        let challenge = try await store.sendEmailCode(email: "user@example.com", purpose: .register)
        XCTAssertEqual(challenge.challengeID, "challenge")
        try await store.resetPassword(email: "user@example.com", password: "password", code: "012345", challengeID: challenge.challengeID)
        XCTAssertNil(store.session)
        XCTAssertNil(tokens.token)
    }

    func testRegistrationInstallationErrorRetainsCleanupFailures() async throws {
        let backend = BackendStub()
        backend.logoutFails = true
        let tokens = TokenStoreStub()
        tokens.saveFails = true
        let store = AuthSessionStore(backend: backend, tokenStore: tokens, deviceID: UUID())
        do { try await store.register(email: "user@example.com", password: "password1234567", code: "012345", challengeID: "challenge"); XCTFail("Expected registration installation error") }
        catch let error as AuthRegistrationError {
            let cleanup = try XCTUnwrap(error.installationError as? AuthCleanupError)
            guard case AuthError.keychain = cleanup.operationError else { return XCTFail("Expected original keychain error") }
            XCTAssertTrue(cleanup.revocationError is URLError)
        }
        XCTAssertNil(store.session)
        XCTAssertEqual(backend.logoutTokens, ["access"])
    }

    func testRegistrationBackendFailuresAreNotReportedAsCompletedRegistration() async throws {
        let backend = BackendStub()
        let store = AuthSessionStore(backend: backend, tokenStore: TokenStoreStub(), deviceID: UUID())
        backend.registerError = URLError(.timedOut)
        do { try await store.register(email: "user@example.com", password: "password1234567", code: "012345", challengeID: "challenge"); XCTFail("Expected network failure") }
        catch is URLError {}
        backend.registerError = AuthError.server(code: "EMAIL_ALREADY_REGISTERED", message: "unavailable")
        do { try await store.register(email: "user@example.com", password: "password1234567", code: "012345", challengeID: "challenge"); XCTFail("Expected registration rejection") }
        catch AuthError.server(let code, _) { XCTAssertEqual(code, "EMAIL_ALREADY_REGISTERED") }
        XCTAssertTrue(backend.logoutTokens.isEmpty)
    }

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
        let first = Task { try await store.refreshIfNeeded() }
        while backend.refreshContinuation == nil { await Task.yield() }
        let second = Task { try await store.refreshIfNeeded() }
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

/// 旧 Google consumer 只实现基础协议，邮箱扩展不能成为迁移要求。
@MainActor
private final class GoogleOnlyBackend: AuthBackend {
    func authenticate(googleIDToken: String, deviceID: UUID) async throws -> AuthTokenResponse {
        AuthTokenResponse(accessToken: "access", refreshToken: "refresh", expiresIn: 900, user: AuthUser(id: UUID(), email: nil, displayName: nil))
    }
    func refresh(refreshToken: String) async throws -> AuthTokenResponse {
        try await authenticate(googleIDToken: "", deviceID: UUID())
    }
    func logout(accessToken: String) async throws {}
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
private final class BackendStub: EmailPasswordAuthBackend, AppleAuthBackend, AppleReauthenticationBackend, AccountManagementAuthBackend {
    func createAppleChallenge(purpose: AppleReauthenticationPurpose, accessToken: String) async throws -> AppleSignInChallenge {
        managementTokens.append(accessToken)
        return try await createAppleChallenge()
    }
    var managementTokens: [String] = []
    var pauseManagement = false
    var managementContinuation: CheckedContinuation<[AuthLoginIdentity], Error>?
    func listIdentities(accessToken: String) async throws -> [AuthLoginIdentity] {
        managementTokens.append(accessToken)
        if pauseManagement { return try await withCheckedThrowingContinuation { managementContinuation = $0 } }
        return []
    }
    func bindExternal(provider: String, credential: String, reauthentication: AuthReauthentication, accessToken: String) async throws { managementTokens.append(accessToken) }
    func unlinkIdentity(_ identity: AuthLoginIdentity, reauthentication: AuthReauthentication, accessToken: String) async throws { managementTokens.append(accessToken) }
    var pauseUpdate = false
    var updateContinuation: CheckedContinuation<AuthTokenResponse, Error>?
    func sendEmailUpdateCode(email: String, reauthentication: AuthReauthentication, accessToken: String) async throws -> EmailCodeChallenge {
        managementTokens.append(accessToken)
        return EmailCodeChallenge(challengeID: "challenge", expiresIn: 300, resendAfter: 60, codeLength: 6)
    }
    func updateEmail(email: String, code: String, challengeID: String, newPassword: String?, accessToken: String) async throws -> AuthTokenResponse {
        if pauseUpdate { return try await withCheckedThrowingContinuation { updateContinuation = $0 } }
        return response
    }
    var response = AuthTokenResponse(accessToken: "access", refreshToken: "refresh", expiresIn: 900, user: AuthUser(id: UUID(), email: "user@example.com", displayName: "User"))
    var receivedRefreshTokens: [String] = []
    var logoutFails = false
    var logoutRejectsCancelledTask = false
    var pauseLogin = false
    var pauseRefresh = false
    var refreshError: Error?
    var resetError: Error?
    var registerError: Error?
    var pauseReset = false
    var logoutTokens: [String] = []
    var logoutRejectedToken: String?
    var loginContinuation: CheckedContinuation<AuthTokenResponse, Error>?
    var refreshContinuation: CheckedContinuation<AuthTokenResponse, Error>?
    var resetContinuation: CheckedContinuation<Void, Error>?
    let appleChallenge = AppleSignInChallenge(challengeID: "apple-challenge", nonce: "raw-nonce", expiresIn: 300)
    var pauseAppleChallenge = false
    var appleChallengeContinuation: CheckedContinuation<AppleSignInChallenge, Error>?
    var appleAuthorization: AppleAuthorization?
    var appleChallengeID: String?
    var appleDeviceID: UUID?
    func createAppleChallenge() async throws -> AppleSignInChallenge {
        if pauseAppleChallenge { return try await withCheckedThrowingContinuation { appleChallengeContinuation = $0 } }
        return appleChallenge
    }
    func authenticate(appleAuthorization: AppleAuthorization, challengeID: String, deviceID: UUID) async throws -> AuthTokenResponse {
        self.appleAuthorization = appleAuthorization
        appleChallengeID = challengeID
        appleDeviceID = deviceID
        return try await authenticate(googleIDToken: "", deviceID: deviceID)
    }
    func sendEmailCode(email: String, purpose: EmailCodePurpose) async throws -> EmailCodeChallenge {
        EmailCodeChallenge(challengeID: "challenge", expiresIn: 600, resendAfter: 60, codeLength: 6)
    }
    func authenticate(email: String, password: String, deviceID: UUID) async throws -> AuthTokenResponse {
        try await authenticate(googleIDToken: "", deviceID: deviceID)
    }
    func register(email: String, password: String, code: String, challengeID: String, deviceID: UUID) async throws -> AuthTokenResponse {
        if let registerError { throw registerError }
        return try await authenticate(googleIDToken: "", deviceID: deviceID)
    }
    func resetPassword(email: String, password: String, code: String, challengeID: String) async throws {
        if let resetError { throw resetError }
        if pauseReset { try await withCheckedThrowingContinuation { resetContinuation = $0 } }
    }
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
        if logoutRejectsCancelledTask { try Task.checkCancellation() }
        logoutTokens.append(accessToken)
        if accessToken == logoutRejectedToken { throw AuthError.server(code: "ACCESS_TOKEN_INVALID", message: "rotated") }
        if logoutFails { throw URLError(.notConnectedToInternet) }
    }
}

/// 系统授权边界替身，支持取消后迟到的原生回调。
@MainActor
private final class AppleProviderStub: AppleAuthorizationProviding {
    let authorization = AppleAuthorization(identityToken: "apple-id-token", authorizationCode: "apple-code", displayName: "Untrusted Name")
    var nonces: [String] = []
    var pause = false
    var continuation: CheckedContinuation<AppleAuthorization, Error>?
    func signIn(nonce: String) async throws -> AppleAuthorization {
        nonces.append(nonce)
        if pause { return try await withCheckedThrowingContinuation { continuation = $0 } }
        return authorization
    }
}
