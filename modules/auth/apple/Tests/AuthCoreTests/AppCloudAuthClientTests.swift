import XCTest
@testable import AuthCore

/// URLProtocol 捕获真实 URLSession 请求，验证应用前缀和 eapi 契约。
@MainActor
final class AppCloudAuthClientTests: XCTestCase {
    func testExchangePreservesApplicationPrefixAndDecodesBackendUser() async throws {
        let deviceID = UUID()
        let userID = UUID()
        let (client, recorder) = try makeClient(response: """
        {"code":"SUCCESS","message":"ok","data":{"access_token":"access","refresh_token":"refresh","token_type":"Bearer","expires_in":900,"user":{"id":"\(userID)","email":null,"display_name":"Name"}},"timestamp":"2026-10-20"}
        """)
        let result = try await client.authenticate(googleIDToken: "google", deviceID: deviceID)
        let request = try XCTUnwrap(recorder.request)
        XCTAssertEqual(request.url?.absoluteString, "https://example.com/adbox/api/v1/auth/google")
        XCTAssertEqual(request.httpMethod, "POST")
        let body = try JSONSerialization.jsonObject(with: recorder.body) as? [String: String]
        XCTAssertEqual(body?["id_token"], "google")
        XCTAssertEqual(body?["device_id"], deviceID.uuidString)
        XCTAssertEqual(result.user.id, userID)
        XCTAssertNil(result.user.email)
    }

    func testLogoutUsesBearerAndNoBody() async throws {
        let (client, recorder) = try makeClient(response: "{\"code\":\"SUCCESS\",\"message\":\"ok\",\"data\":null}")
        try await client.logout(accessToken: "opaque-token")
        XCTAssertEqual(recorder.request?.value(forHTTPHeaderField: "Authorization"), "Bearer opaque-token")
        XCTAssertTrue(recorder.body.isEmpty)
        XCTAssertEqual(recorder.request?.url?.path, "/adbox/api/v1/auth/logout")
    }

    func testServerFailureDoesNotCreateSession() async throws {
        let (client, _) = try makeClient(response: "{\"code\":\"AUTH_FAILED\",\"message\":\"invalid\",\"data\":null}", status: 401)
        do {
            _ = try await client.refresh(refreshToken: "refresh")
            XCTFail("Expected server error")
        } catch let AuthError.server(code, _) { XCTAssertEqual(code, "AUTH_FAILED") }
    }

    func testRejectsInsecureRemoteBackend() {
        XCTAssertThrowsError(try AppCloudAuthClient(baseURL: URL(string: "http://example.com/adbox")!))
    }

    func testUnicodeProfileUsesBackendCharacterLimits() async throws {
        let name = String(repeating: "名", count: 255)
        let email = String(repeating: "用", count: 110) + "@example.com"
        let (client, _) = try makeClient(response: """
        {"code":"SUCCESS","message":"ok","data":{"access_token":"access","refresh_token":"refresh","token_type":"Bearer","expires_in":900,"user":{"id":"\(UUID())","email":"\(email)","display_name":"\(name)"}}}
        """)
        let result = try await client.refresh(refreshToken: "refresh")
        XCTAssertEqual(result.user.displayName, name)
        XCTAssertEqual(result.user.email, email)
    }

    /// 每个 session 单独绑定 recorder，测试并行不会共享可变 handler。
    private func makeClient(response: String, status: Int = 200) throws -> (AppCloudAuthClient, RequestRecorder) {
        let recorder = RequestRecorder(response: Data(response.utf8), status: status)
        let config = URLSessionConfiguration.ephemeral
        config.protocolClasses = [StubURLProtocol.self]
        let identifier = UUID().uuidString
        StubURLProtocol.registry.insert(recorder, id: identifier)
        config.httpAdditionalHeaders = ["X-Test-ID": identifier]
        let session = URLSession(configuration: config)
        return (try AppCloudAuthClient(baseURL: URL(string: "https://example.com/adbox")!, session: session), recorder)
    }
}

/// 锁保护 URLSession 工作线程写入的请求证据。
private final class RequestRecorder: NSObject, URLSessionDelegate, @unchecked Sendable {
    let response: Data
    let status: Int
    private let lock = NSLock()
    private var recordedRequest: URLRequest?
    private var recordedBody = Data()
    init(response: Data, status: Int) { self.response = response; self.status = status }
    var request: URLRequest? { lock.withLock { recordedRequest } }
    var body: Data { lock.withLock { recordedBody } }
    func record(_ request: URLRequest) {
        var body = request.httpBody ?? Data()
        if let stream = request.httpBodyStream {
            stream.open()
            defer { stream.close() }
            var buffer = [UInt8](repeating: 0, count: 1024)
            while stream.hasBytesAvailable {
                let count = stream.read(&buffer, maxLength: buffer.count)
                if count <= 0 { break }
                body.append(buffer, count: count)
            }
        }
        lock.withLock { recordedRequest = request; recordedBody = body }
    }
}

/// 不访问网络的 URLProtocol；Swift 6 下只透传 Sendable recorder。
private final class StubURLProtocol: URLProtocol, @unchecked Sendable {
    static let registry = RecorderRegistry()
    override class func canInit(with request: URLRequest) -> Bool { true }
    override class func canonicalRequest(for request: URLRequest) -> URLRequest { request }
    override func startLoading() {
        guard let identifier = request.value(forHTTPHeaderField: "X-Test-ID"), let recorder = Self.registry.take(id: identifier) else {
            client?.urlProtocol(self, didFailWithError: URLError(.unknown))
            return
        }
        recorder.record(request)
        let response = HTTPURLResponse(url: request.url!, statusCode: recorder.status, httpVersion: nil, headerFields: ["Content-Type": "application/json"])!
        client?.urlProtocol(self, didReceive: response, cacheStoragePolicy: .notAllowed)
        client?.urlProtocol(self, didLoad: recorder.response)
        client?.urlProtocolDidFinishLoading(self)
    }
    override func stopLoading() {}
}

/// 注册表在请求开始时移除记录，避免静态测试数据跨用例累积。
private final class RecorderRegistry: @unchecked Sendable {
    private let lock = NSLock()
    private var recorders: [String: RequestRecorder] = [:]
    func insert(_ recorder: RequestRecorder, id: String) { lock.withLock { recorders[id] = recorder } }
    func take(id: String) -> RequestRecorder? { lock.withLock { recorders.removeValue(forKey: id) } }
}
