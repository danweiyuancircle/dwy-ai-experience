import Foundation

/// 应用后端认证 HTTP 客户端；baseURL 的 /adbox 等应用前缀必须保留。
@MainActor
public final class AppCloudAuthClient: AuthBackend {
    public let baseURL: URL
    private let session: URLSession

    /// 生产只接受 HTTPS；本机开发允许明确的 loopback HTTP。
    public init(baseURL: URL, session: URLSession = .shared) throws {
        guard baseURL.host != nil, baseURL.user == nil, baseURL.password == nil,
              baseURL.query == nil, baseURL.fragment == nil,
              baseURL.scheme == "https" || (baseURL.scheme == "http" && ["localhost", "127.0.0.1", "::1"].contains(baseURL.host))
        else { throw AuthError.invalidConfiguration }
        self.baseURL = baseURL
        self.session = session
    }

    /// ID token 仅用于本次后端交换，设备 UUID 不参与认证证明。
    public func authenticate(googleIDToken: String, deviceID: UUID) async throws -> AuthTokenResponse {
        guard !googleIDToken.isEmpty, googleIDToken.utf8.count <= 16_384 else { throw AuthError.invalidResponse }
        let body = GoogleBody(idToken: googleIDToken, deviceID: deviceID)
        return try await exchange(path: "google", body: JSONEncoder().encode(body))
    }

    /// 后端轮换 refresh token；调用方必须保存返回的新 token。
    public func refresh(refreshToken: String) async throws -> AuthTokenResponse {
        guard !refreshToken.isEmpty, refreshToken.utf8.count <= 4_096 else { throw AuthError.invalidResponse }
        return try await exchange(path: "refresh", body: JSONEncoder().encode(RefreshBody(refreshToken: refreshToken)))
    }

    /// 后端撤销当前会话；本地清理由 AuthSessionStore 先行完成。
    public func logout(accessToken: String) async throws {
        guard !accessToken.isEmpty, accessToken.utf8.count <= 4_096,
              !accessToken.contains(where: { $0.isWhitespace || $0.isNewline })
        else { throw AuthError.invalidResponse }
        _ = try await request(path: "logout", body: nil, accessToken: accessToken)
    }

    /// 键名只在 HTTP 边界转换，业务模型使用 Swift 风格。
    private func exchange(path: String, body: Data) async throws -> AuthTokenResponse {
        let data = try await request(path: path, body: body, accessToken: nil)
        let decoder = JSONDecoder()
        decoder.keyDecodingStrategy = .convertFromSnakeCase
        let envelope: TokenEnvelope
        do { envelope = try decoder.decode(TokenEnvelope.self, from: data) }
        catch is DecodingError { throw AuthError.invalidResponse }
        guard let tokens = envelope.data, tokens.tokenType == "Bearer",
              !tokens.accessToken.isEmpty, tokens.accessToken.utf8.count <= 4_096,
              !tokens.refreshToken.isEmpty, tokens.refreshToken.utf8.count <= 4_096,
              tokens.expiresIn.isFinite, tokens.expiresIn > 0,
              (tokens.user.email?.count ?? 0) <= 320,
              (tokens.user.displayName?.count ?? 0) <= 255
        else { throw AuthError.invalidResponse }
        return AuthTokenResponse(accessToken: tokens.accessToken, refreshToken: tokens.refreshToken, expiresIn: tokens.expiresIn, user: tokens.user)
    }

    /// 先验证状态与 eapi 信封；错误 message 不直接展示，避免后端内部细节进入 UI。
    private func request(path: String, body: Data?, accessToken: String?) async throws -> Data {
        let url = baseURL.appendingPathComponent("api/v1/auth").appendingPathComponent(path)
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.timeoutInterval = 30
        request.httpBody = body
        request.setValue("application/json", forHTTPHeaderField: "Accept")
        if body != nil { request.setValue("application/json", forHTTPHeaderField: "Content-Type") }
        if let accessToken { request.setValue("Bearer \(accessToken)", forHTTPHeaderField: "Authorization") }
        let (data, response) = try await session.data(for: request)
        guard let http = response as? HTTPURLResponse, data.count <= 65_536 else { throw AuthError.invalidResponse }
        let envelope: StatusEnvelope
        do { envelope = try JSONDecoder().decode(StatusEnvelope.self, from: data) }
        catch is DecodingError { throw AuthError.invalidResponse }
        guard (200..<300).contains(http.statusCode), envelope.code == "SUCCESS" else {
            throw AuthError.server(code: envelope.code, message: String(envelope.message.prefix(500)))
        }
        return data
    }
}

/// 固定 schema 避免松散字典把不受支持字段传到认证服务。
private struct GoogleBody: Encodable {
    let idToken: String
    let deviceID: UUID
    enum CodingKeys: String, CodingKey { case idToken = "id_token", deviceID = "device_id" }
}
private struct RefreshBody: Encodable {
    let refreshToken: String
    enum CodingKeys: String, CodingKey { case refreshToken = "refresh_token" }
}
/// eapi 状态先于业务 payload 验证，错误信封无需伪造 token data。
private struct StatusEnvelope: Decodable {
    let code: String
    let message: String
}
/// 仅解交换 payload，timestamp 由服务端使用且不参与客户端有效期判断。
private struct TokenEnvelope: Decodable {
    let data: TokenData?
}
/// 后端 token schema 的内部表示，不泄露 snake_case 到公共 API。
private struct TokenData: Decodable {
    let accessToken: String
    let refreshToken: String
    let tokenType: String
    let expiresIn: TimeInterval
    let user: AuthUser
}
