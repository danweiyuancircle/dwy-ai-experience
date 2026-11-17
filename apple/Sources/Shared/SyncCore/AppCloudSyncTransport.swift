import Foundation

/// app-cloud HTTP 适配；保留应用基路径，响应在读取过程中执行字节上限。
public struct AppCloudSyncTransport: SyncTransport {
    /// 唯一网络目标与账号来源，禁止和数据库作用域分开配置。
    public let scope: SyncScope
    private let session: URLSession
    private let maxResponseBytes: Int

    /// scope.backendURL 必须包含实际应用路径；appID 与存储保持相同有界约束。
    public init(scope: SyncScope, session: URLSession = .shared, maxResponseBytes: Int = 4_194_304) throws {
        let baseURL = scope.backendURL
        guard let components = URLComponents(url: baseURL, resolvingAgainstBaseURL: false),
              let scheme = components.scheme?.lowercased(), ["https", "http"].contains(scheme),
              let host = components.host?.lowercased(), !host.isEmpty,
              components.user == nil, components.password == nil,
              components.query == nil, components.fragment == nil,
              components.port.map({ (1...65_535).contains($0) }) != false,
              scheme == "https" || Self.isLoopback(host), maxResponseBytes > 0,
              !scope.appID.isEmpty, scope.appID.utf8.count <= 100
        else { throw SyncTransportError.invalidBaseURL }
        self.scope = scope
        self.session = session
        self.maxResponseBytes = maxResponseBytes
    }

    /// 单条冻结 mutation 发送后校验回执对应操作和文档，防止错误确认队列。
    public func push(_ mutation: SyncMutation, identity: SyncIdentity) async throws -> SyncPushResult {
        try validate(identity)
        guard mutation.baseVersion >= 0, mutation.baseVersion <= Int64.max - 1,
              SyncWireValidation.validPayload(mutation.payload, deleted: mutation.deleted)
        else { throw SyncTransportError.invalidRequest }
        let body: Data
        do { body = try JSONEncoder().encode(PushBody(mutations: [mutation])) }
        catch { throw SyncTransportError.invalidRequest }
        guard body.count <= SyncWireValidation.maxPayloadBytes + 1_024 else { throw SyncTransportError.invalidRequest }
        let result: SyncPushResult = try await request("push", identity: identity, body: body)
        guard result.cursor >= 0, result.items.count == 1, let item = result.items.first,
              item.operationID == mutation.operationID else { throw SyncTransportError.invalidResponse }
        switch item.status {
        case .applied:
            guard let record = item.record, item.reasonCode == nil, record.recordID == mutation.recordID,
                  SyncWireValidation.validRecord(record), record.cursor <= result.cursor,
                  record.version == mutation.baseVersion + 1,
                  record.deleted == mutation.deleted, record.payload == mutation.payload else {
                throw SyncTransportError.invalidResponse
            }
        case .rejected:
            guard item.record == nil, item.reasonCode == "write_retired" else { throw SyncTransportError.invalidResponse }
        }
        return result
    }

    /// 拉取固定最多100条；只接受严格递增游标和不重复的文档快照。
    public func pull(cursor: Int64, identity: SyncIdentity) async throws -> SyncPullPage {
        try validate(identity)
        guard cursor >= 0 else { throw SyncTransportError.invalidRequest }
        let page: SyncPullPage = try await request("pull", identity: identity, cursor: cursor)
        guard page.items.count <= 100, page.nextCursor >= cursor,
              !page.hasMore || !page.items.isEmpty
        else { throw SyncTransportError.invalidResponse }
        var previous = cursor
        var seen = Set<UUID>()
        for record in page.items {
            guard SyncWireValidation.validRecord(record), record.cursor > previous,
                  record.cursor <= page.nextCursor, seen.insert(record.recordID).inserted
            else { throw SyncTransportError.invalidResponse }
            previous = record.cursor
        }
        // 仍有后续页时使用最后一条 cursor；最后一页可推进到服务端高水位。
        guard !page.hasMore || page.nextCursor == previous else { throw SyncTransportError.invalidResponse }
        return page
    }

    /// 游客禁止请求，可信账号必须与固定 scope 一致；有界 ASCII 令牌防止 Header 注入。
    private func validate(_ identity: SyncIdentity) throws {
        guard let scopedUser = scope.userID, identity.userID == scopedUser,
              !identity.accessToken.isEmpty, identity.accessToken.utf8.count <= 4_096,
              identity.accessToken.utf8.allSatisfy({ (33...126).contains($0) })
        else { throw SyncTransportError.invalidIdentity }
    }

    /// 所有错误仅返回固定分类或有界信封字段，不附带 Authorization 或原始正文。
    private func request<Result: Decodable>(
        _ endpoint: String, identity: SyncIdentity, body: Data? = nil, cursor: Int64? = nil
    ) async throws -> Result {
        let url = scope.backendURL.appendingPathComponent("api/v1/sync").appendingPathComponent(endpoint)
        guard var components = URLComponents(url: url, resolvingAgainstBaseURL: false) else {
            throw SyncTransportError.invalidBaseURL
        }
        if let cursor { components.queryItems = [.init(name: "cursor", value: String(cursor)), .init(name: "limit", value: "100")] }
        guard let requestURL = components.url else { throw SyncTransportError.invalidBaseURL }
        var request = URLRequest(url: requestURL)
        request.httpMethod = body == nil ? "GET" : "POST"
        request.httpBody = body
        request.timeoutInterval = 30
        request.setValue("application/json", forHTTPHeaderField: "Accept")
        request.setValue("Bearer \(identity.accessToken)", forHTTPHeaderField: "Authorization")
        if body != nil { request.setValue("application/json", forHTTPHeaderField: "Content-Type") }
        let (bytes, response) = try await session.bytes(for: request, delegate: SyncNoRedirectDelegate())
        // 读取中提前失败或调用方取消时，立即取消底层下载。
        defer { bytes.task.cancel() }
        guard let http = response as? HTTPURLResponse else { throw SyncTransportError.invalidResponse }
        guard response.expectedContentLength <= Int64(maxResponseBytes) else { throw SyncTransportError.responseTooLarge }
        var data = Data()
        for try await byte in bytes {
            guard data.count < maxResponseBytes else { throw SyncTransportError.responseTooLarge }
            data.append(byte)
        }
        let decoder = JSONDecoder()
        let status: StatusEnvelope
        do { status = try decoder.decode(StatusEnvelope.self, from: data) }
        catch {
            if !(200..<300).contains(http.statusCode) {
                throw SyncServerError(statusCode: http.statusCode, code: "http_error", message: "同步服务请求失败", retryAfter: Self.retryAfter(http))
            }
            throw SyncTransportError.invalidResponse
        }
        guard !status.code.isEmpty, status.code.utf8.count <= 128, status.message.utf8.count <= 2_048 else {
            throw SyncTransportError.invalidResponse
        }
        guard (200..<300).contains(http.statusCode), status.code == "SUCCESS" else {
            let conflict: ConflictEnvelope
            do { conflict = try decoder.decode(ConflictEnvelope.self, from: data) }
            catch { throw SyncTransportError.invalidResponse }
            if let current = conflict.data?.current, !SyncWireValidation.validRecord(current) { throw SyncTransportError.invalidResponse }
            throw SyncServerError(
                statusCode: http.statusCode,
                code: status.code.replacingOccurrences(of: identity.accessToken, with: "[redacted]"),
                message: status.message.replacingOccurrences(of: identity.accessToken, with: "[redacted]"),
                operationID: conflict.data?.operationID, current: conflict.data?.current,
                retryAfter: Self.retryAfter(http)
            )
        }
        do { return try decoder.decode(DataEnvelope<Result>.self, from: data).data }
        catch { throw SyncTransportError.invalidResponse }
    }

    /// 不解析 DNS；仅接受明确的 localhost、IPv4 127/8 和 IPv6 ::1。
    private static func isLoopback(_ host: String) -> Bool {
        if ["localhost", "::1", "[::1]"].contains(host) { return true }
        let octets = host.split(separator: ".", omittingEmptySubsequences: false)
        return octets.count == 4 && octets.first == "127" && octets.allSatisfy {
            !$0.isEmpty && $0.utf8.allSatisfy({ (48...57).contains($0) }) && UInt8($0) != nil
        }
    }

    /// 服务端 Retry-After 同时支持秒数与标准 HTTP 日期，解析失败不造默认值。
    private static func retryAfter(_ response: HTTPURLResponse) -> TimeInterval? {
        guard let value = response.value(forHTTPHeaderField: "Retry-After") else { return nil }
        if let seconds = TimeInterval(value), seconds.isFinite, seconds >= 0 { return seconds }
        let formatter = DateFormatter()
        formatter.locale = Locale(identifier: "en_US_POSIX")
        formatter.timeZone = TimeZone(secondsFromGMT: 0)
        formatter.dateFormat = "EEE, dd MMM yyyy HH:mm:ss z"
        guard let date = formatter.date(from: value) else { return nil }
        return max(0, date.timeIntervalSinceNow)
    }

}

/// 禁止认证请求自动跳转，避免重定向到不同服务或明文 HTTP。
private final class SyncNoRedirectDelegate: NSObject, URLSessionTaskDelegate, @unchecked Sendable {
    func urlSession(_ session: URLSession, task: URLSessionTask, willPerformHTTPRedirection response: HTTPURLResponse,
                    newRequest request: URLRequest, completionHandler: @escaping @Sendable (URLRequest?) -> Void) {
        completionHandler(nil)
    }
}

/// 上传信封不携带 owner/device；服务端身份来自验证过的 Bearer。
private struct PushBody: Encodable { let mutations: [SyncMutation] }
/// 先解状态码，再决定成功数据或冲突数据，避免按 HTTP 409 猜错误种类。
private struct StatusEnvelope: Decodable { let code: String; let message: String }
/// 成功数据必须存在且符合完整 Codable 合同。
private struct DataEnvelope<Value: Decodable>: Decodable { let data: Value }
/// 普通服务错误允许 null data，内容冲突提供 operation_id 和 current。
private struct ConflictEnvelope: Decodable { let data: ConflictData? }
/// 冲突快照仍须经过文档验证，不能把任意 JSON 传给存储。
private struct ConflictData: Decodable {
    let operationID: UUID
    let current: SyncRecord?
    enum CodingKeys: String, CodingKey { case operationID = "operation_id", current }
}
