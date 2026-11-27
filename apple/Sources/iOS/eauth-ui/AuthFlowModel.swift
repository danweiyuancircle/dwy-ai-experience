import Foundation
import Observation
import AuthCore

enum AuthFlowMode: Equatable {
    case login, register, resetPassword
}

enum AuthFlowMessage: String {
    case invalidEmail, invalidPassword, invalidNewPassword, requestCode, invalidCode, codeExpired
    case codeSent, passwordReset, invalidCredentials, emailRegistered, rateLimited, requestFailed
    case registrationCompleted, storageFailed
    case purchaseRequired, purchaseLinked, purchaseVerificationFailed
}

@MainActor
public struct AuthFlowActions {
    let sendCode: (String, EmailCodePurpose) async throws -> EmailCodeChallenge
    let signIn: (String, String) async throws -> AuthUser
    let register: (String, String, String, String) async throws -> AuthUser
    let resetPassword: (String, String, String, String) async throws -> Void
    let cancel: () -> Void

    public init(session: AuthSessionStore) {
        sendCode = { try await session.sendEmailCode(email: $0, purpose: $1) }
        signIn = {
            try await session.signIn(email: $0, password: $1)
            guard let user = session.session?.user else { throw AuthError.signedOut }
            return user
        }
        register = {
            try await session.register(email: $0, password: $1, code: $2, challengeID: $3)
            guard let user = session.session?.user else { throw AuthError.signedOut }
            return user
        }
        resetPassword = { try await session.resetPassword(email: $0, password: $1, code: $2, challengeID: $3) }
        cancel = { session.cancelPendingAuthentication() }
    }

    /// 宿主注入业务生命周期动作；共享 UI 不直接安装或缓存令牌。
    public init(
        sendCode: @escaping (String, EmailCodePurpose) async throws -> EmailCodeChallenge,
        signIn: @escaping (String, String) async throws -> AuthUser,
        register: @escaping (String, String, String, String) async throws -> AuthUser,
        resetPassword: @escaping (String, String, String, String) async throws -> Void,
        cancel: @escaping () -> Void
    ) {
        self.sendCode = sendCode
        self.signIn = signIn
        self.register = register
        self.resetPassword = resetPassword
        self.cancel = cancel
    }
}

/// 页面状态独立于宿主导航；时间和认证边界可注入，密码只驻留内存。
@MainActor
@Observable
final class AuthFlowModel {
    var email = "" {
        didSet {
            guard email != oldValue else { return }
            invalidate()
            message = nil
        }
    }
    var password = ""
    var code = ""
    private(set) var mode: AuthFlowMode = .login
    private(set) var challenge: EmailCodeChallenge?
    private(set) var isBusy = false
    private(set) var message: AuthFlowMessage?
    @ObservationIgnored private let actions: AuthFlowActions
    @ObservationIgnored private let now: () -> Date
    @ObservationIgnored private var generation = 0
    @ObservationIgnored private var expiresAt: Date?
    @ObservationIgnored private var resendAt: Date?

    init(actions: AuthFlowActions, now: @escaping () -> Date = Date.init) {
        self.actions = actions
        self.now = now
    }

    var isNotice: Bool { [.codeSent, .passwordReset, .registrationCompleted].contains(message) }

    func switchMode(_ mode: AuthFlowMode) {
        invalidate()
        password = ""
        self.mode = mode
        message = nil
    }

    func sendCode() async {
        guard !isBusy, mode != .login, resendSeconds(at: now()) == 0 else { return }
        guard EmailPasswordRules.isValidEmail(email) else { message = .invalidEmail; return }
        let operation = generation
        let purpose: EmailCodePurpose = mode == .register ? .register : .passwordReset
        isBusy = true
        message = nil
        defer { if generation == operation { isBusy = false } }
        do {
            let response = try await actions.sendCode(EmailPasswordRules.normalizedEmail(email), purpose)
            guard generation == operation else { return }
            challenge = response
            code = ""
            expiresAt = now().addingTimeInterval(response.expiresIn)
            resendAt = now().addingTimeInterval(response.resendAfter)
            message = .codeSent
        } catch {
            guard generation == operation else { return }
            message = errorMessage(error)
        }
    }

    func submit() async -> AuthUser? {
        guard !isBusy else { return nil }
        guard EmailPasswordRules.isValidEmail(email) else { message = .invalidEmail; return nil }
        if mode == .login {
            guard EmailPasswordRules.isValidLoginPassword(password) else { message = .invalidPassword; return nil }
        } else {
            guard EmailPasswordRules.isValidNewPassword(password) else { message = .invalidNewPassword; return nil }
            guard let challenge, let expiresAt else { message = .requestCode; return nil }
            guard expiresAt > now() else { message = .codeExpired; return nil }
            guard code.utf8.count == challenge.codeLength, code.utf8.allSatisfy({ (48...57).contains($0) }) else {
                message = .invalidCode
                return nil
            }
        }
        let operation = generation
        let submittedMode = mode
        isBusy = true
        message = nil
        defer { if generation == operation { isBusy = false } }
        do {
            let address = EmailPasswordRules.normalizedEmail(email)
            let user: AuthUser?
            switch submittedMode {
            case .login:
                user = try await actions.signIn(address, password)
            case .register:
                guard let challenge else { return nil }
                user = try await actions.register(address, password, code, challenge.challengeID)
            case .resetPassword:
                guard let challenge else { return nil }
                try await actions.resetPassword(address, password, code, challenge.challengeID)
                user = nil
            }
            guard generation == operation else { return nil }
            password = ""
            code = ""
            challenge = nil
            if submittedMode == .resetPassword {
                mode = .login
                message = .passwordReset
            }
            return user
        } catch {
            guard generation == operation else { return nil }
            if submittedMode == .register, error is AuthRegistrationError {
                switchMode(.login)
                message = .registrationCompleted
            } else {
                message = errorMessage(error)
            }
            return nil
        }
    }

    func resendSeconds(at date: Date) -> Int {
        guard let resendAt else { return 0 }
        return max(0, Int(ceil(resendAt.timeIntervalSince(date))))
    }

    func cancel() {
        invalidate()
        password = ""
        message = nil
    }

    /// 在原生授权面板打开前取票据；重复点击和关闭页面不能启动第二次请求。
    func beginExternalSignIn() -> Int? {
        guard !isBusy else { return nil }
        message = nil
        isBusy = true
        return generation
    }

    /// Google 获取凭据与后端交换共用一次可取消操作。
    func signIn(using action: @MainActor () async throws -> AuthUser) async -> AuthUser? {
        guard let operation = beginExternalSignIn() else { return nil }
        return await completeExternalSignIn(operation: operation, using: action)
    }

    /// Apple 授权回调可能晚于页面退出，调用业务前先核对操作仍然有效。
    func completeExternalSignIn(operation: Int, using action: @MainActor () async throws -> AuthUser) async -> AuthUser? {
        guard operation == generation, isBusy else { return nil }
        defer { if operation == generation { isBusy = false } }
        do {
            let user = try await action()
            guard operation == generation else { return nil }
            password = ""
            code = ""
            challenge = nil
            return user
        } catch {
            guard operation == generation else { return nil }
            if !(error is CancellationError) { message = errorMessage(error) }
            return nil
        }
    }

    private func invalidate() {
        generation += 1
        actions.cancel()
        challenge = nil
        code = ""
        expiresAt = nil
        resendAt = nil
        isBusy = false
    }

    private func errorMessage(_ error: any Error) -> AuthFlowMessage {
        if error is AuthCleanupError { return .storageFailed }
        guard case let AuthError.server(code, _) = error else { return .requestFailed }
        switch code.uppercased() {
        case "PURCHASE_REQUIRED", "IAP_PURCHASE_REQUIRED", "IAP_PURCHASE_INACTIVE", "CLOUD_PURCHASE_REQUIRED", "CLOUD_SUBSCRIPTION_REQUIRED": return .purchaseRequired
        case "IAP_OWNERSHIP_CONFLICT": return .purchaseLinked
        case "IAP_UNAVAILABLE", "APPLE_UNAVAILABLE", "IAP_SIGNATURE_INVALID", "IAP_OWNERSHIP_REQUIRED", "AUTH_ADMISSION_PROOF_INVALID", "CLOUD_PURCHASE_VERIFICATION_REQUIRED", "CLOUD_PURCHASE_VERIFICATION_FAILED": return .purchaseVerificationFailed
        case "CREDENTIALS_INVALID": return .invalidCredentials
        case "EMAIL_ALREADY_REGISTERED": return .emailRegistered
        case "EMAIL_CODE_INVALID": return .invalidCode
        case "EMAIL_RATE_LIMITED": return .rateLimited
        case "EMAIL_INVALID": return .invalidEmail
        case "PASSWORD_INVALID": return mode == .login ? .invalidPassword : .invalidNewPassword
        default: return .requestFailed
        }
    }
}
