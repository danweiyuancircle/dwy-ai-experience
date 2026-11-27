#if os(iOS)
import AuthenticationServices
import AuthCore
import UIKit

/// AuthenticationServices 原生适配；宿主提供当前窗口，不探测全局 scene。
@MainActor
public final class AppleSignInProvider: AppleAuthorizationProviding {
    private let presentationAnchor: () -> ASPresentationAnchor?
    private let makeController: ([ASAuthorizationRequest]) -> ASAuthorizationController
    private var active: AuthorizationOperation?

    /// provider 应由宿主持有；一次授权保活 controller/delegate，Task 取消会关闭系统授权。
    public convenience init(presentationAnchor: @escaping () -> ASPresentationAnchor?) {
        self.init(presentationAnchor: presentationAnchor, makeController: ASAuthorizationController.init(authorizationRequests:))
    }

    init(presentationAnchor: @escaping () -> ASPresentationAnchor?, makeController: @escaping ([ASAuthorizationRequest]) -> ASAuthorizationController) {
        self.presentationAnchor = presentationAnchor
        self.makeController = makeController
    }

    /// nonce 必须直接使用目标应用挑战值；Apple 短时凭据仅用于服务端交换。
    public func signIn(nonce: String) async throws -> AppleAuthorization {
        try Task.checkCancellation()
        guard active == nil else { throw AuthError.superseded }
        guard !nonce.isEmpty, nonce.utf8.count <= 4_096 else { throw AuthError.invalidResponse }
        guard let anchor = presentationAnchor() else { throw AuthError.invalidConfiguration }
        let request = ASAuthorizationAppleIDProvider().createRequest()
        request.nonce = nonce
        request.requestedScopes = [.fullName, .email]
        let controller = makeController([request])
        let operationID = UUID()
        return try await withTaskCancellationHandler {
            try await withCheckedThrowingContinuation { continuation in
                guard !Task.isCancelled else {
                    continuation.resume(throwing: CancellationError())
                    return
                }
                let delegate = AuthorizationDelegate(anchor: anchor) { [weak self] controller, result in
                    self?.complete(controller: controller, result: result)
                }
                active = AuthorizationOperation(id: operationID, controller: controller, delegate: delegate, continuation: continuation)
                controller.delegate = delegate
                controller.presentationContextProvider = delegate
                controller.performRequests()
            }
        } onCancel: {
            Task { @MainActor [weak self] in
                guard let self, let operation = self.active, operation.id == operationID else { return }
                self.complete(controller: operation.controller, result: .failure(CancellationError()))
                operation.controller.cancel()
            }
        }
    }

    private func complete(controller: ASAuthorizationController, result: Result<AppleAuthorization, any Error>) {
        guard let operation = active, operation.controller === controller else { return }
        active = nil
        controller.delegate = nil
        controller.presentationContextProvider = nil
        operation.continuation.resume(with: result)
    }
}

@MainActor
private struct AuthorizationOperation {
    let id: UUID
    let controller: ASAuthorizationController
    let delegate: AuthorizationDelegate
    let continuation: CheckedContinuation<AppleAuthorization, any Error>
}

/// 系统的两个 delegate 引用都是 weak，必须由在途操作明确持有。
@MainActor
private final class AuthorizationDelegate: NSObject, ASAuthorizationControllerDelegate, ASAuthorizationControllerPresentationContextProviding {
    private let anchor: ASPresentationAnchor
    private let completion: (ASAuthorizationController, Result<AppleAuthorization, any Error>) -> Void

    init(anchor: ASPresentationAnchor, completion: @escaping (ASAuthorizationController, Result<AppleAuthorization, any Error>) -> Void) {
        self.anchor = anchor
        self.completion = completion
    }

    func presentationAnchor(for controller: ASAuthorizationController) -> ASPresentationAnchor { anchor }

    func authorizationController(controller: ASAuthorizationController, didCompleteWithAuthorization authorization: ASAuthorization) {
        guard let credential = authorization.credential as? ASAuthorizationAppleIDCredential else {
            completion(controller, .failure(AuthError.invalidResponse))
            return
        }
        do {
            let result = try decodeAppleAuthorization(identityToken: credential.identityToken, authorizationCode: credential.authorizationCode, fullName: credential.fullName)
            completion(controller, .success(result))
        } catch {
            completion(controller, .failure(error))
        }
    }

    func authorizationController(controller: ASAuthorizationController, didCompleteWithError error: any Error) {
        if let authorizationError = error as? ASAuthorizationError, authorizationError.code == .canceled {
            completion(controller, .failure(CancellationError()))
        } else {
            completion(controller, .failure(error))
        }
    }
}

func decodeAppleAuthorization(identityToken: Data?, authorizationCode: Data?, fullName: PersonNameComponents?) throws -> AppleAuthorization {
    guard let identityToken, let token = String(data: identityToken, encoding: .utf8), !token.isEmpty,
          let authorizationCode, let code = String(data: authorizationCode, encoding: .utf8), !code.isEmpty
    else { throw AuthError.invalidResponse }
    let name = fullName.map { PersonNameComponentsFormatter().string(from: $0).trimmingCharacters(in: .whitespacesAndNewlines) }
    return AppleAuthorization(identityToken: token, authorizationCode: code, displayName: name?.isEmpty == false ? name : nil)
}
#endif
