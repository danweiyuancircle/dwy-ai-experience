import XCTest
import AuthCore
@testable import AuthUI

@MainActor
final class AuthFlowModelTests: XCTestCase {
    /// 授权面板退出后迟到的 Apple 凭据不能重新启动一次登录。
    func testCancelledExternalAuthorizationNeverInvokesSignIn() async throws {
        let model = makeModel()
        let operation = try XCTUnwrap(model.beginExternalSignIn())
        XCTAssertTrue(model.isBusy)
        XCTAssertNil(model.beginExternalSignIn())
        model.cancel()
        var invoked = false
        let result = await model.completeExternalSignIn(operation: operation) { invoked = true; return self.user }
        XCTAssertNil(result)
        XCTAssertFalse(invoked)
    }

    /// 第三方登录也通过同一状态机，成功清理密码，错误只显示安全固定文案。
    func testExternalSignInClearsSecretsAndMapsPurchaseConflict() async {
        let model = makeModel()
        model.password = password
        let result = await model.signIn { self.user }
        XCTAssertEqual(result, user)
        XCTAssertTrue(model.password.isEmpty)
        let rejected = await model.signIn { throw AuthError.server(code: "iap_ownership_conflict", message: "do not show owner") }
        XCTAssertNil(rejected)
        XCTAssertEqual(model.message?.rawValue, "purchaseLinked")
    }
    private let user = AuthUser(id: UUID(), email: "person@example.com", displayName: nil)
    private let password = "long secure password"

    func testInvalidEmailDoesNotSubmit() async {
        let model = makeModel()
        model.email = "invalid"
        model.password = password
        let result = await model.submit()
        XCTAssertNil(result)
        XCTAssertEqual(model.message, .invalidEmail)
    }

    func testRegistrationReturnsAuthenticatedUserAndClearsSecrets() async {
        let model = makeModel()
        model.switchMode(.register)
        model.email = "person@example.com"
        model.password = password
        await model.sendCode()
        model.code = "123456"
        let result = await model.submit()
        XCTAssertEqual(result, user)
        XCTAssertTrue(model.password.isEmpty)
        XCTAssertTrue(model.code.isEmpty)
        XCTAssertNil(model.challenge)
    }

    func testChangingEmailInvalidatesPreviouslySentChallenge() async {
        let model = makeModel()
        model.switchMode(.register)
        model.email = "first@example.com"
        await model.sendCode()
        XCTAssertNotNil(model.challenge)
        model.email = "second@example.com"
        XCTAssertNil(model.challenge)
        model.password = password
        model.code = "123456"
        let result = await model.submit()
        XCTAssertNil(result)
        XCTAssertEqual(model.message, .requestCode)
    }

    func testRegistrationRejectsShortAndOversizedUTF8Passwords() async {
        let model = makeModel()
        model.switchMode(.register)
        model.email = "person@example.com"
        model.password = "short"
        let shortResult = await model.submit()
        XCTAssertNil(shortResult)
        XCTAssertEqual(model.message, .invalidNewPassword)
        model.password = String(repeating: "密", count: 25)
        let oversizedResult = await model.submit()
        XCTAssertNil(oversizedResult)
        XCTAssertEqual(model.message, .invalidNewPassword)
    }

    func testResetReturnsToLoginWithoutAuthenticating() async {
        let model = makeModel()
        model.switchMode(.resetPassword)
        model.email = "person@example.com"
        model.password = password
        await model.sendCode()
        model.code = "123456"
        let result = await model.submit()
        XCTAssertNil(result)
        XCTAssertEqual(model.mode, .login)
        XCTAssertEqual(model.message, .passwordReset)
        XCTAssertTrue(model.password.isEmpty)
    }

    func testCooldownAndExpiryUseInjectedClock() async {
        var current = Date(timeIntervalSince1970: 1000)
        let model = makeModel(now: { current })
        model.switchMode(.register)
        model.email = "person@example.com"
        await model.sendCode()
        XCTAssertEqual(model.resendSeconds(at: current), 60)
        current.addTimeInterval(61)
        XCTAssertEqual(model.resendSeconds(at: current), 0)
        model.password = password
        model.code = "123456"
        current.addTimeInterval(300)
        let result = await model.submit()
        XCTAssertNil(result)
        XCTAssertEqual(model.message, .codeExpired)
    }

    func testCanceledLoginCannotReturnLateUserOrRestoreSecrets() async {
        var continuation: CheckedContinuation<AuthUser, any Error>?
        let actions = AuthFlowActions(
            sendCode: { _, _ in self.challenge },
            signIn: { _, _ in try await withCheckedThrowingContinuation { continuation = $0 } },
            register: { _, _, _, _ in self.user },
            resetPassword: { _, _, _, _ in },
            cancel: {}
        )
        let model = AuthFlowModel(actions: actions)
        model.email = "person@example.com"
        model.password = password
        let task = Task { await model.submit() }
        for _ in 0..<1000 {
            if continuation != nil { break }
            await Task.yield()
        }
        guard let pending = continuation else {
            task.cancel()
            XCTFail("Login did not reach the authentication boundary")
            return
        }
        model.cancel()
        pending.resume(returning: user)
        let result = await task.value
        XCTAssertNil(result)
        XCTAssertFalse(model.isBusy)
        XCTAssertTrue(model.password.isEmpty)
    }

    func testUnknownServerErrorDoesNotExposeRawMessage() async {
        let actions = AuthFlowActions(
            sendCode: { _, _ in self.challenge },
            signIn: { _, _ in throw AuthError.server(code: "UNKNOWN", message: "secret detail") },
            register: { _, _, _, _ in self.user },
            resetPassword: { _, _, _, _ in },
            cancel: {}
        )
        let model = AuthFlowModel(actions: actions)
        model.email = "person@example.com"
        model.password = password
        let result = await model.submit()
        XCTAssertNil(result)
        XCTAssertEqual(model.message, .requestFailed)
        XCTAssertFalse(model.isBusy)
    }

    func testLocalizedComponentCopyIsAvailableInBothLanguages() {
        XCTAssertEqual(AuthStrings.text("login", locale: Locale(identifier: "en")), "Sign in")
        XCTAssertEqual(AuthStrings.text("login", locale: Locale(identifier: "zh-Hans")), "登录")
    }

    func testRegisteredAccountWithInstallationFailureReturnsToLogin() async {
        let actions = AuthFlowActions(
            sendCode: { _, _ in self.challenge },
            signIn: { _, _ in self.user },
            register: { _, _, _, _ in throw AuthRegistrationError(installationError: AuthError.keychain(-50)) },
            resetPassword: { _, _, _, _ in },
            cancel: {}
        )
        let model = AuthFlowModel(actions: actions)
        model.switchMode(.register)
        model.email = "person@example.com"
        model.password = password
        await model.sendCode()
        model.code = "123456"
        let result = await model.submit()
        XCTAssertNil(result)
        XCTAssertEqual(model.mode, .login)
        XCTAssertEqual(model.message, .registrationCompleted)
        XCTAssertTrue(model.password.isEmpty)
    }

    private var challenge: EmailCodeChallenge {
        EmailCodeChallenge(challengeID: UUID().uuidString, expiresIn: 300, resendAfter: 60, codeLength: 6)
    }

    private func makeModel(now: @escaping () -> Date = Date.init) -> AuthFlowModel {
        AuthFlowModel(actions: AuthFlowActions(
            sendCode: { _, _ in self.challenge },
            signIn: { _, _ in self.user },
            register: { _, _, _, _ in self.user },
            resetPassword: { _, _, _, _ in },
            cancel: {}
        ), now: now)
    }
}
