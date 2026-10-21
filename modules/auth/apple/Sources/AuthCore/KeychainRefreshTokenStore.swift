import Foundation
import Security
import CryptoKit

/// 单活动账号 refresh token；应用 namespace 与完整后端 URL 隔离 Keychain service。
/// 不设置共享 access group，也不经 iCloud 同步；Google 凭证由 SDK 自己管理。
@MainActor
public final class KeychainRefreshTokenStore: RefreshTokenStoring {
    private let service: String
    private let account = "active-account-refresh-token"

    public init(namespace: String, backendURL: URL) throws {
        guard !namespace.isEmpty, namespace.utf8.count <= 200 else { throw AuthError.invalidConfiguration }
        let scope = SHA256.hash(data: Data(backendURL.absoluteString.trimmingCharacters(in: CharacterSet(charactersIn: "/")).utf8))
            .map { String(format: "%02x", $0) }.joined()
        service = namespace + ".auth." + scope
    }

    /// 无记录返回 nil；存储权限或数据损坏必须抛错，不能假装已退出。
    public func load() throws -> String? {
        var query = identity
        query[kSecReturnData] = true
        query[kSecMatchLimit] = kSecMatchLimitOne
        var result: CFTypeRef?
        let status = SecItemCopyMatching(query as CFDictionary, &result)
        if status == errSecItemNotFound { return nil }
        guard status == errSecSuccess else { throw AuthError.keychain(status) }
        guard let data = result as? Data, let token = String(data: data, encoding: .utf8),
              !token.isEmpty, data.count <= 4_096 else { throw AuthError.invalidResponse }
        return token
    }

    /// 更新同一个活动账号槽位，refresh 轮换不先删除旧记录。
    public func save(_ token: String) throws {
        guard !token.isEmpty, token.utf8.count <= 4_096 else { throw AuthError.invalidResponse }
        let attributes: [CFString: Any] = [
            kSecValueData: Data(token.utf8),
            kSecAttrAccessible: kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly,
        ]
        let updated = SecItemUpdate(identity as CFDictionary, attributes as CFDictionary)
        if updated == errSecSuccess { return }
        guard updated == errSecItemNotFound else { throw AuthError.keychain(updated) }
        let item = identity.merging(attributes) { _, value in value }
        let status = SecItemAdd(item as CFDictionary, nil)
        guard status == errSecSuccess else { throw AuthError.keychain(status) }
    }

    /// 删除幂等；除不存在外的系统失败保留为可提示错误。
    public func delete() throws {
        let status = SecItemDelete(identity as CFDictionary)
        guard status == errSecSuccess || status == errSecItemNotFound else { throw AuthError.keychain(status) }
    }

    /// 固定单账号槽位避免切换用户后遗留上一账号 refresh token。
    private var identity: [CFString: Any] {
        [kSecClass: kSecClassGenericPassword, kSecAttrService: service, kSecAttrAccount: account, kSecAttrSynchronizable: false]
    }
}

/// 安装级设备标识只用于后端会话关联，不能作为登录凭证或设备证明。
@MainActor
public enum AuthDeviceIdentity {
    /// 每个应用保持稳定安装 ID；不跨应用共享、不用作认证凭据。
    public static func loadOrCreate(namespace: String, defaults: UserDefaults = .standard) throws -> UUID {
        guard !namespace.isEmpty, namespace.utf8.count <= 200 else { throw AuthError.invalidConfiguration }
        let key = namespace + ".auth.device-id"
        if let raw = defaults.string(forKey: key), let value = UUID(uuidString: raw) { return value }
        let value = UUID()
        defaults.set(value.uuidString, forKey: key)
        return value
    }
}
