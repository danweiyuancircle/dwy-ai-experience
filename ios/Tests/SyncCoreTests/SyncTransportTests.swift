import Foundation
import XCTest
@testable import SyncCore

/// URLProtocol 合同测试覆盖真实 URLSession 编码、信封与流式读取边界。
final class SyncTransportTests: XCTestCase, @unchecked Sendable {
    private let userID = UUID(uuidString: "11111111-1111-1111-1111-111111111111")!
    private let deviceID = UUID(uuidString: "22222222-2222-2222-2222-222222222222")!
    private let recordID = UUID(uuidString: "33333333-3333-3333-3333-333333333333")!
    private let operationID = UUID(uuidString: "44444444-4444-4444-4444-444444444444")!

    /// 请求只发送 mutations；服务端从 Bearer 身份解析 owner 与 device。
    func testPushPreservesBasePathAndSnakeCaseAndInt64Precision() async throws {
        let version = Int64.max - 2
        let record = SyncRecord(recordID: recordID, version: version + 1, cursor: Int64.max,
                                deleted: false, payload: ["kind": .string("note"), "count": .integer(Int64.max)])
        let result = SyncPushResult(items: [.init(operationID: operationID, record: record, replayed: false)], cursor: Int64.max)
        let session = stub(try envelope(result))
        defer { session.invalidateAndCancel() }
        let transport = try AppCloudSyncTransport(scope: scope("https://example.com/adbox"), session: session, maxResponseBytes: 65_536)
        let mutation = SyncMutation(operationID: operationID, recordID: recordID, baseVersion: version,
                                    deleted: false, payload: record.payload)
        let actual = try await transport.push(mutation, identity: identity)
        XCTAssertEqual(actual, result)
        let request = try XCTUnwrap(SyncStubProtocol.state.request)
        XCTAssertEqual(request.url?.absoluteString, "https://example.com/adbox/api/v1/sync/push")
        XCTAssertEqual(request.httpMethod, "POST")
        XCTAssertEqual(request.value(forHTTPHeaderField: "Authorization"), "Bearer test-token")
        let body = try XCTUnwrap(request.httpBody)
        let object = try XCTUnwrap(JSONSerialization.jsonObject(with: body) as? [String: Any])
        XCTAssertEqual(Set(object.keys), ["mutations"])
        let item = try XCTUnwrap((object["mutations"] as? [[String: Any]])?.first)
        XCTAssertEqual(Set(item.keys), ["operation_id", "record_id", "base_version", "deleted", "payload"])
        XCTAssertTrue(String(decoding: body, as: UTF8.self).contains("9223372036854775807"))
        XCTAssertTrue(String(decoding: body, as: UTF8.self).contains("9223372036854775805"))
    }

    /// 拉取合同使用 items / next_cursor / has_more，游标始终作为 Int64 解码。
    func testPullUsesEnvelopeAndFixedLimit() async throws {
        let page = SyncPullPage(items: [], nextCursor: Int64.max, hasMore: false)
        let session = stub(try envelope(page))
        defer { session.invalidateAndCancel() }
        let transport = try AppCloudSyncTransport(scope: scope("http://127.0.0.1:8000/adbox/"), session: session, maxResponseBytes: 65_536)
        let actual = try await transport.pull(cursor: Int64.max, identity: identity)
        XCTAssertEqual(actual, page)
        XCTAssertEqual(SyncStubProtocol.state.request?.url?.absoluteString,
                       "http://127.0.0.1:8000/adbox/api/v1/sync/pull?cursor=9223372036854775807&limit=100")
    }

    /// 最后一页使用服务端高水位，允许高水位超过当前返回记录游标。
    func testPullAcceptsFinalHighWatermark() async throws {
        let page = SyncPullPage(items: [], nextCursor: 7, hasMore: false)
        let session = stub(try envelope(page))
        defer { session.invalidateAndCancel() }
        let transport = try AppCloudSyncTransport(scope: scope("https://example.com/adbox"), session: session, maxResponseBytes: 1024)
        let actual = try await transport.pull(cursor: 1, identity: identity)
        XCTAssertEqual(actual, page)
    }

    /// 同一 HTTP 409 必须保留 code，不能把配额和幂等错误伪造成内容冲突。
    func testServerErrorsKeepCodeAndConflictSnapshotAndRetryAfter() async throws {
        for code in ["version_conflict", "operation_reused", "record_quota_exceeded"] {
            let data = Data("{\"code\":\"\(code)\",\"message\":\"safe\",\"data\":{\"operation_id\":\"\(operationID)\",\"current\":null}}".utf8)
            let session = stub(data, status: 409, headers: ["Retry-After": "3"])
            defer { session.invalidateAndCancel() }
            let transport = try AppCloudSyncTransport(scope: scope("https://example.com/adbox"), session: session, maxResponseBytes: 65_536)
            do {
                _ = try await transport.pull(cursor: 0, identity: identity)
                XCTFail("应返回类型化服务错误")
            } catch let error as SyncServerError {
                XCTAssertEqual(error.code, code)
                XCTAssertEqual(error.statusCode, 409)
                XCTAssertEqual(error.operationID, operationID)
                XCTAssertEqual(error.retryAfter, 3)
            }
        }
    }

    /// 外部 URL 必须完整；明文 HTTP 限本机，不接受凭据或附带查询。
    func testRejectsUnsafeBaseURLs() {
        for url in ["http://example.com/adbox", "https://user:pass@example.com/adbox", "https://example.com/adbox?q=1", "https://example.com/adbox#x", "/adbox", "file:///adbox"] {
            XCTAssertThrowsError(try AppCloudSyncTransport(scope: scope(url), session: .shared, maxResponseBytes: 1024))
        }
        XCTAssertThrowsError(try AppCloudSyncTransport(scope: scope("https://example.com"), session: .shared, maxResponseBytes: 0))
    }

    /// 身份和游标错误须在发请求前拒绝，错误描述不得含 Bearer 内容。
    func testRejectsInvalidIdentityCursorAndMutationBeforeSending() async throws {
        let session = stub(Data())
        defer { session.invalidateAndCancel() }
        let transport = try AppCloudSyncTransport(scope: scope("https://example.com/adbox"), session: session, maxResponseBytes: 1024)
        for token in ["", "test-token\r\nInjected: yes", String(repeating: "x", count: 4097)] {
            await assertFailure(.invalidIdentity) { _ = try await transport.pull(cursor: 0, identity: SyncIdentity(userID: self.userID, deviceID: self.deviceID, accessToken: token)) }
        }
        await assertFailure(.invalidRequest) { _ = try await transport.pull(cursor: -1, identity: self.identity) }
        let mutation = SyncMutation(operationID: operationID, recordID: recordID, baseVersion: Int64.max, deleted: true, payload: nil)
        await assertFailure(.invalidRequest) { _ = try await transport.push(mutation, identity: self.identity) }
        XCTAssertNil(SyncStubProtocol.state.request)
    }

    /// 逐字节读取时超限立即失败，不能先收完整个服务端正文再检查大小。
    func testRejectsOversizedResponse() async throws {
        for headers in [["Content-Length": "4096"], [:]] {
            let session = stub(Data(repeating: 32, count: 4096), headers: headers)
            defer { session.invalidateAndCancel() }
            let transport = try AppCloudSyncTransport(scope: scope("https://example.com/adbox"), session: session, maxResponseBytes: 128)
            await assertFailure(.responseTooLarge) { _ = try await transport.pull(cursor: 0, identity: self.identity) }
        }
    }

    /// 不可信远端的类型、删除状态、kind 与页边界必须全部校验。
    func testRejectsMalformedPullPages() async throws {
        let good = "{\"record_id\":\"\(recordID)\",\"version\":1,\"cursor\":2,\"deleted\":false,\"payload\":{\"kind\":\"note\"}}"
        let invalid = [
            "{\"items\":[],\"next_cursor\":0,\"has_more\":false}",
            "{\"items\":[],\"next_cursor\":1,\"has_more\":true}",
            "{\"items\":[\(good),\(good)],\"next_cursor\":2,\"has_more\":false}",
            "{\"items\":[\(good.replacingOccurrences(of: "\"kind\":\"note\"", with: ""))],\"next_cursor\":2,\"has_more\":false}",
            "{\"items\":[\(good.replacingOccurrences(of: "false", with: "true"))],\"next_cursor\":2,\"has_more\":false}",
            "{\"items\":[\(good.replacingOccurrences(of: "\"version\":1", with: "\"version\":9223372036854775808"))],\"next_cursor\":2,\"has_more\":false}",
            "{\"items\":[\(good.replacingOccurrences(of: "\"version\":1", with: "\"version\":true"))],\"next_cursor\":2,\"has_more\":false}"
        ]
        for page in invalid {
            let session = stub(Data("{\"code\":\"SUCCESS\",\"message\":\"ok\",\"data\":\(page)}".utf8))
            defer { session.invalidateAndCancel() }
            let transport = try AppCloudSyncTransport(scope: scope("https://example.com/adbox"), session: session, maxResponseBytes: 65_536)
            await assertFailure(.invalidResponse) { _ = try await transport.pull(cursor: 1, identity: self.identity) }
        }
    }

    /// JSON 整数独立于 Double 表示，不能把 Int64 高位静默舍入。
    func testJSONPreservesIntegerAndRejectsNonFiniteNumber() throws {
        let json: SyncJSON = .object(["large": .integer(Int64.max), "fraction": .number(0.25), "flag": .bool(true), "empty": .null])
        XCTAssertEqual(try JSONDecoder().decode(SyncJSON.self, from: JSONEncoder().encode(json)), json)
        XCTAssertThrowsError(try JSONEncoder().encode(SyncJSON.number(.infinity)))
    }

    /// 服务端若回显凭据，公开错误与身份调试输出仍须隐藏令牌。
    func testRedactsTokenFromErrorsAndIdentityDescription() async throws {
        let session = stub(Data("{\"code\":\"unauthorized\",\"message\":\"rejected test-token\",\"data\":null}".utf8), status: 401)
        defer { session.invalidateAndCancel() }
        let transport = try AppCloudSyncTransport(scope: scope("https://example.com/adbox"), session: session, maxResponseBytes: 1024)
        do {
            _ = try await transport.pull(cursor: 0, identity: identity)
            XCTFail("应返回未授权错误")
        } catch let error as SyncServerError {
            XCTAssertFalse(error.message.contains(identity.accessToken))
            XCTAssertFalse(String(describing: error).contains(identity.accessToken))
        }
        XCTAssertFalse(String(describing: identity).contains(identity.accessToken))
        XCTAssertFalse(String(reflecting: identity).contains(identity.accessToken))
    }

    /// 删除请求显式发送 null，错误 operationID 的回执不能误确认本地队列。
    func testDeletedMutationUsesNullAndRejectsMismatchedReceipt() async throws {
        let record = SyncRecord(recordID: recordID, version: 1, cursor: 1, deleted: true, payload: nil)
        let result = SyncPushResult(items: [.init(operationID: UUID(), record: record, replayed: true)], cursor: 1)
        let session = stub(try envelope(result))
        defer { session.invalidateAndCancel() }
        let transport = try AppCloudSyncTransport(scope: scope("https://example.com/adbox"), session: session, maxResponseBytes: 1024)
        let mutation = SyncMutation(operationID: operationID, recordID: recordID, baseVersion: 0, deleted: true, payload: nil)
        await assertFailure(.invalidResponse) { _ = try await transport.push(mutation, identity: self.identity) }
        let body = try XCTUnwrap(SyncStubProtocol.state.request?.httpBody)
        let object = try XCTUnwrap(JSONSerialization.jsonObject(with: body) as? [String: Any])
        let item = try XCTUnwrap((object["mutations"] as? [[String: Any]])?.first)
        XCTAssertTrue(item["payload"] is NSNull)
    }

    /// 传输目标由完整 scope 决定，不能另传一个与数据库作用域无关的地址。
    func testTransportPublishesScopeAndUsesItsBackendURL() async throws {
        let expectedScope = scope("https://stage.example.com/other-app")
        let page = SyncPullPage(items: [], nextCursor: 0, hasMore: false)
        let session = stub(try envelope(page))
        defer { session.invalidateAndCancel() }
        let transport = try AppCloudSyncTransport(scope: expectedScope, session: session, maxResponseBytes: 1024)
        let contract: any SyncTransport = transport
        XCTAssertEqual(contract.scope, expectedScope)
        _ = try await transport.pull(cursor: 0, identity: identity)
        XCTAssertEqual(SyncStubProtocol.state.request?.url?.absoluteString,
                       "https://stage.example.com/other-app/api/v1/sync/pull?cursor=0&limit=100")
    }

    /// 错误账号和游客 scope 均必须在请求发出前拒绝，避免跨账号读写。
    func testRejectsMismatchedIdentityAndGuestScopeBeforeSending() async throws {
        let session = stub(Data())
        defer { session.invalidateAndCancel() }
        let backendURL = URL(string: "https://example.com/adbox")!
        for scopedUser in [UUID(), Optional<UUID>.none] {
            let scope = SyncScope(backendURL: backendURL, appID: "adbox", userID: scopedUser)
            let transport = try AppCloudSyncTransport(scope: scope, session: session, maxResponseBytes: 1024)
            await assertFailure(.invalidIdentity) { _ = try await transport.pull(cursor: 0, identity: self.identity) }
            let mutation = SyncMutation(operationID: operationID, recordID: recordID, baseVersion: 0, deleted: true, payload: nil)
            await assertFailure(.invalidIdentity) { _ = try await transport.push(mutation, identity: self.identity) }
        }
        XCTAssertNil(SyncStubProtocol.state.request)
    }

    /// appID 参与本地隔离键，不能接受空值或超过存储边界的标识符。
    func testRejectsUnboundedApplicationID() {
        for appID in ["", String(repeating: "a", count: 101)] {
            let scope = SyncScope(backendURL: URL(string: "https://example.com/adbox")!, appID: appID, userID: userID)
            XCTAssertThrowsError(try AppCloudSyncTransport(scope: scope, session: .shared, maxResponseBytes: 1024))
        }
    }

    /// 测试沿用固定账号，只改变明确传入的后端应用地址。
    private func scope(_ url: String) -> SyncScope {
        .init(backendURL: URL(string: url)!, appID: "adbox", userID: userID)
    }

    private var identity: SyncIdentity { .init(userID: userID, deviceID: deviceID, accessToken: "test-token") }

    /// 统一成功信封，数据仍通过生产 Codable 合同序列化。
    private func envelope<T: Encodable>(_ value: T) throws -> Data {
        let payload = try JSONEncoder().encode(value)
        return Data("{\"code\":\"SUCCESS\",\"message\":\"ok\",\"data\":".utf8) + payload + Data("}".utf8)
    }

    /// 每例替换协议状态，禁止真实网络请求。
    private func stub(_ data: Data, status: Int = 200, headers: [String: String] = [:]) -> URLSession {
        SyncStubProtocol.state.configure(data: data, status: status, headers: headers)
        let configuration = URLSessionConfiguration.ephemeral
        configuration.protocolClasses = [SyncStubProtocol.self]
        return URLSession(configuration: configuration)
    }

    /// 明确断言错误类别，避免仅“有任意错误”掩盖错误的失败原因。
    private func assertFailure(_ expected: SyncTransportError, operation: () async throws -> Void, file: StaticString = #filePath, line: UInt = #line) async {
        do { try await operation(); XCTFail("应拒绝非法输入或响应", file: file, line: line) }
        catch let error as SyncTransportError { XCTAssertEqual(error, expected, file: file, line: line) }
        catch { XCTFail("错误类型不符: \(type(of: error))", file: file, line: line) }
    }
}

/// URLSession 回调跨线程，测试夹具仅通过锁读写共享状态。
private final class SyncStubState: @unchecked Sendable {
    private let lock = NSLock()
    private var value = (data: Data(), status: 200, headers: [String: String](), request: Optional<URLRequest>.none)
    var request: URLRequest? { lock.withLock { value.request } }
    func configure(data: Data, status: Int, headers: [String: String]) { lock.withLock { value = (data, status, headers, nil) } }
    func capture(_ request: URLRequest) -> (Data, Int, [String: String]) {
        lock.withLock { value.request = request; return (value.data, value.status, value.headers) }
    }
}

/// 将有限测试字节交给 URLSession，适用于 bytes(for:) 正式读取路径。
private final class SyncStubProtocol: URLProtocol, @unchecked Sendable {
    static let state = SyncStubState()
    override class func canInit(with request: URLRequest) -> Bool { true }
    override class func canonicalRequest(for request: URLRequest) -> URLRequest { request }
    override func startLoading() {
        // URLSession 把 POST body 转成流后仍须检查实际发送内容。
        var captured = request
        if captured.httpBody == nil, let stream = captured.httpBodyStream {
            stream.open()
            defer { stream.close() }
            var body = Data()
            var buffer = [UInt8](repeating: 0, count: 4096)
            while stream.hasBytesAvailable {
                let count = stream.read(&buffer, maxLength: buffer.count)
                if count <= 0 { break }
                body.append(contentsOf: buffer.prefix(count))
            }
            captured.httpBody = body
        }
        let (data, status, headers) = Self.state.capture(captured)
        client?.urlProtocol(self, didReceive: HTTPURLResponse(url: request.url!, statusCode: status, httpVersion: nil, headerFields: headers)!, cacheStoragePolicy: .notAllowed)
        client?.urlProtocol(self, didLoad: data)
        client?.urlProtocolDidFinishLoading(self)
    }
    override func stopLoading() {}
}
