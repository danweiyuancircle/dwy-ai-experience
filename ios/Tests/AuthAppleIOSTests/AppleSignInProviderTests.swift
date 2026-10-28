#if os(iOS)
import XCTest
import AuthenticationServices
import UIKit
import AuthCore
@testable import AuthAppleIOS

/// 系统 UI 由控制器边界替身隔离；请求与委托生命周期仍走真实适配器。
@MainActor
final class AppleSignInProviderTests: XCTestCase {
    func testCredentialDecodingPreservesTokenAndCodeWithOptionalName() throws {
        var name = PersonNameComponents()
        name.givenName = "Ada"
        for fullName: PersonNameComponents? in [nil, PersonNameComponents(), name] {
            let authorization = try decodeAppleAuthorization(identityToken: Data("identity-token".utf8), authorizationCode: Data("one-time-code".utf8), fullName: fullName)
            XCTAssertEqual(authorization.identityToken, "identity-token")
            XCTAssertEqual(authorization.authorizationCode, "one-time-code")
            XCTAssertEqual(authorization.displayName, fullName?.givenName)
        }
    }

    func testCredentialDecodingRejectsMissingEmptyAndNonUTF8Material() throws {
        let valid = Data("valid".utf8)
        for invalid: Data? in [nil, Data(), Data([0xff])] {
            XCTAssertThrowsError(try decodeAppleAuthorization(identityToken: invalid, authorizationCode: valid, fullName: nil)) { error in
                guard case AuthError.invalidResponse = error else { return XCTFail("Expected invalid credential") }
            }
            XCTAssertThrowsError(try decodeAppleAuthorization(identityToken: valid, authorizationCode: invalid, fullName: nil)) { error in
                guard case AuthError.invalidResponse = error else { return XCTFail("Expected invalid credential") }
            }
        }
    }

    func testUnexpectedSystemErrorIsNotReportedAsCancellation() async throws {
        var controller: AuthorizationControllerStub?
        let window = UIWindow()
        let provider = AppleSignInProvider(presentationAnchor: { window }, makeController: { requests in
            let result = AuthorizationControllerStub(authorizationRequests: requests)
            controller = result
            return result
        })
        let login = Task { try await provider.signIn(nonce: "nonce") }
        while controller == nil { await Task.yield() }
        let active = try XCTUnwrap(controller)
        active.delegate?.authorizationController?(controller: active, didCompleteWithError: ASAuthorizationError(.failed))
        do { _ = try await login.value; XCTFail("Expected system error") }
        catch let error as ASAuthorizationError { XCTAssertEqual(error.code, .failed) }
    }

    func testRequestUsesRawNonceHostAnchorAndRetainsDelegateUntilCancellation() async throws {
        let window = UIWindow()
        var controller: AuthorizationControllerStub?
        let provider = AppleSignInProvider(presentationAnchor: { window }, makeController: { requests in
            let result = AuthorizationControllerStub(authorizationRequests: requests)
            controller = result
            return result
        })
        let login = Task { try await provider.signIn(nonce: "raw_nonce-123") }
        while controller == nil { await Task.yield() }
        let active = try XCTUnwrap(controller)
        let request = try XCTUnwrap(active.authorizationRequests.first as? ASAuthorizationAppleIDRequest)
        XCTAssertEqual(request.nonce, "raw_nonce-123")
        XCTAssertEqual(request.requestedScopes, [.fullName, .email])
        XCTAssertTrue(active.presentationContextProvider?.presentationAnchor(for: active) === window)
        XCTAssertNotNil(active.delegate)
        login.cancel()
        do { _ = try await login.value; XCTFail("Expected task cancellation") } catch is CancellationError {}
        XCTAssertTrue(active.didCancel)
    }

    func testSystemCancellationBecomesCancellationErrorAndCanRetry() async throws {
        var controllers: [AuthorizationControllerStub] = []
        let window = UIWindow()
        let provider = AppleSignInProvider(presentationAnchor: { window }, makeController: { requests in
            let result = AuthorizationControllerStub(authorizationRequests: requests)
            controllers.append(result)
            return result
        })
        let first = Task { try await provider.signIn(nonce: "first") }
        while controllers.isEmpty { await Task.yield() }
        do { _ = try await provider.signIn(nonce: "duplicate"); XCTFail("Expected concurrent request rejection") }
        catch AuthError.superseded {}
        let old = controllers[0]
        let delegate = try XCTUnwrap(old.delegate)
        delegate.authorizationController?(controller: old, didCompleteWithError: ASAuthorizationError(.canceled))
        do { _ = try await first.value; XCTFail("Expected system cancellation") } catch is CancellationError {}
        let retry = Task { try await provider.signIn(nonce: "second") }
        while controllers.count < 2 { await Task.yield() }
        // 原控制器的迟到回调不能完成新请求。
        delegate.authorizationController?(controller: old, didCompleteWithError: ASAuthorizationError(.failed))
        retry.cancel()
        do { _ = try await retry.value; XCTFail("Expected retry cancellation") } catch is CancellationError {}
        XCTAssertTrue(controllers[1].didCancel)
    }

    func testMissingAnchorAndInvalidNonceFailBeforePresentation() async throws {
        let provider = AppleSignInProvider(presentationAnchor: { nil })
        do { _ = try await provider.signIn(nonce: "nonce"); XCTFail("Expected host anchor") }
        catch AuthError.invalidConfiguration {}
        let window = UIWindow()
        let anchored = AppleSignInProvider(presentationAnchor: { window })
        for nonce in ["", String(repeating: "n", count: 4_097)] {
            do { _ = try await anchored.signIn(nonce: nonce); XCTFail("Expected bounded nonce") }
            catch AuthError.invalidResponse {}
        }
    }
}

private final class AuthorizationControllerStub: ASAuthorizationController {
    var didCancel = false
    override func performRequests() {}
    override func cancel() { didCancel = true }
}
#endif
