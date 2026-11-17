#if os(iOS)
import LocalAuthentication
import PermissionIOS

public extension IOSPermissions {
    /// 生物识别是一次认证操作，不提供伪造的长期授权状态；reason 必须向用户说明用途。
    static func authenticateWithBiometrics(reason: String) async throws -> Bool {
        guard !reason.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else {
            throw IOSPermissionError.emptyAuthenticationReason
        }
        let context = LAContext()
        var error: NSError?
        guard context.canEvaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, error: &error) else {
            if let error { throw error }
            return false
        }
        if context.biometryType == .faceID { try validateUsageDescriptions(["NSFaceIDUsageDescription"]) }
        return try await context.evaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, localizedReason: reason)
    }
}
#endif
