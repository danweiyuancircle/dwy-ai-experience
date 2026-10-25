import XCTest
@testable import AuthCore

/// URLProtocol 捕获真实 URLSession 请求，验证应用前缀和 eapi 契约。
@MainActor
final class AppCloudAuthClientTests: XCTestCase {
    /// 默认语言由本次系统首选决定，不依赖 URLSession 隐式添加请求头。
    func testRequestsExplicitlySendSystemLanguage() async throws {
        let (client, recorder) = try makeClient(response: "{\"code\":\"SUCCESS\",\"message\":\"ok\",\"data\":null}")
        try await client.logout(accessToken: "opaque-token")
        let language = Locale.preferredLanguages.first?.lowercased()
        let expected = language == "zh" || language?.hasPrefix("zh-") == true ? "zh" : "en"
        XCTAssertEqual(recorder.request?.value(forHTTPHeaderField: "Accept-Language"), expected)
    }

    /// 中文变体发送中文，其余语言与缺失值发送英文，不把地区代码当作语言。
    func testEmailCodeLanguageUsesOnlyChineseOrEnglish() async throws {
        let cases: [(String?, String)] = [
            ("zh", "zh"), ("zh-CN", "zh"), ("zh-Hans-CN", "zh"), ("zh-Hant-TW", "zh"),
            ("ZH-Hant-HK", "zh"), ("en-US", "en"), ("ja-JP", "en"), ("vi-VN", "en"),
            ("CN", "en"), ("zhong", "en"), ("", "en"), (nil, "en"),
        ]
        for (language, expected) in cases {
            let (client, recorder) = try makeClient(response: """
            {"code":"SUCCESS","message":"ok","data":{"challenge_id":"id","expires_in":600,"resend_after":60,"code_length":6}}
            """, languageProvider: { language })
            _ = try await client.sendEmailCode(email: "user@example.com", purpose: .register)
            XCTAssertEqual(recorder.request?.value(forHTTPHeaderField: "Accept-Language"), expected, "Language: \(language ?? "nil")")
        }
    }

    /// 同一客户端在后续请求重新读取语言，宿主切换语言后无需重建客户端。
    func testLanguageProviderIsReadForEveryRequest() async throws {
        let language = PreferredLanguageSource("en-US")
        let (client, recorder) = try makeClient(response: "{\"code\":\"SUCCESS\",\"message\":\"ok\",\"data\":null}", languageProvider: { language.value })
        try await client.logout(accessToken: "opaque-token")
        XCTAssertEqual(recorder.request?.value(forHTTPHeaderField: "Accept-Language"), "en")

        let identifier = try XCTUnwrap(recorder.request?.value(forHTTPHeaderField: "X-Test-ID"))
        StubURLProtocol.registry.insert(recorder, id: identifier)
        language.value = "zh-Hans"
        try await client.logout(accessToken: "opaque-token")
        XCTAssertEqual(recorder.request?.value(forHTTPHeaderField: "Accept-Language"), "zh")
    }

    func testEmailChallengeEncodingPreservesPrefixAndDecodesChallenge() async throws {
        let (client, recorder) = try makeClient(response: """
        {"code":"SUCCESS","message":"ok","data":{"challenge_id":"opaque-id","expires_in":600,"resend_after":60,"code_length":6}}
        """)
        let challenge = try await client.sendEmailCode(email: " USER@Example.com ", purpose: .passwordReset)
        XCTAssertEqual(recorder.request?.url?.path, "/adbox/api/v1/auth/email/code")
        XCTAssertEqual(recorder.request?.httpMethod, "POST")
        let body = try JSONSerialization.jsonObject(with: recorder.body) as? [String: String]
        XCTAssertEqual(body, ["email": "user@example.com", "purpose": "password_reset"])
        XCTAssertEqual(challenge.challengeID, "opaque-id")
        XCTAssertEqual(challenge.expiresIn, 600)
        XCTAssertEqual(challenge.resendAfter, 60)
        XCTAssertEqual(challenge.codeLength, 6)
    }

    func testRejectsInvalidChallengePayloads() async throws {
        for payload in ["null", "{}", "{\"challenge_id\":\"\",\"expires_in\":600,\"resend_after\":60,\"code_length\":6}", "{\"challenge_id\":\"id\",\"expires_in\":0,\"resend_after\":60,\"code_length\":6}", "{\"challenge_id\":\"id\",\"expires_in\":600,\"resend_after\":-1,\"code_length\":6}", "{\"challenge_id\":\"id\",\"expires_in\":600,\"resend_after\":60,\"code_length\":0}"] {
            let (client, _) = try makeClient(response: "{\"code\":\"SUCCESS\",\"message\":\"ok\",\"data\":\(payload)}")
            do { _ = try await client.sendEmailCode(email: "user@example.com", purpose: .register); XCTFail("Expected invalid challenge") }
            catch AuthError.invalidResponse {}
        }
    }

    func testEmailLoginAndRegisterEncodeOnlyContractFields() async throws {
        let deviceID = UUID()
        for path in ["login", "register"] {
            let (client, recorder) = try makeClient(response: """
            {"code":"SUCCESS","message":"ok","data":{"access_token":"access","refresh_token":"refresh","token_type":"Bearer","expires_in":900,"user":{"id":"\(UUID())","email":"user@example.com","display_name":null}}}
            """)
            if path == "login" {
                _ = try await client.authenticate(email: "user@example.com", password: " password ", deviceID: deviceID)
            } else {
                _ = try await client.register(email: "user@example.com", password: " password long ", code: "012345", challengeID: "challenge", deviceID: deviceID)
            }
            XCTAssertEqual(recorder.request?.url?.path, "/adbox/api/v1/auth/\(path)")
            let body = try XCTUnwrap(JSONSerialization.jsonObject(with: recorder.body) as? [String: String])
            XCTAssertEqual(body["password"], path == "login" ? " password " : " password long ")
            XCTAssertEqual(body["device_id"], deviceID.uuidString)
            XCTAssertEqual(Set(body.keys), path == "login" ? ["email", "password", "device_id"] : ["email", "password", "device_id", "code", "challenge_id"])
        }
    }

    func testResetPasswordRequiresCompletedStatusAndDoesNotReturnTokens() async throws {
        let (client, recorder) = try makeClient(response: "{\"code\":\"SUCCESS\",\"message\":\"ok\",\"data\":{\"status\":\"completed\"}}")
        try await client.resetPassword(email: "user@example.com", password: "password1234567", code: "012345", challengeID: "challenge")
        XCTAssertEqual(recorder.request?.url?.path, "/adbox/api/v1/auth/password/reset")
        let body = try JSONSerialization.jsonObject(with: recorder.body) as? [String: String]
        XCTAssertEqual(body, ["email": "user@example.com", "password": "password1234567", "code": "012345", "challenge_id": "challenge"])
        let (invalid, _) = try makeClient(response: "{\"code\":\"SUCCESS\",\"message\":\"ok\",\"data\":{\"status\":\"pending\"}}")
        do { try await invalid.resetPassword(email: "user@example.com", password: "password1234567", code: "012345", challengeID: "challenge"); XCTFail("Expected completed status") }
        catch AuthError.invalidResponse {}
    }

    func testPasswordLimitUsesUTF8BytesWithoutTruncation() async throws {
        let (client, recorder) = try makeClient(response: "{\"code\":\"SUCCESS\",\"message\":\"ok\",\"data\":{\"status\":\"completed\"}}")
        try await client.resetPassword(email: "user@example.com", password: String(repeating: "密", count: 24), code: "012345", challengeID: "challenge")
        let body = try JSONSerialization.jsonObject(with: recorder.body) as? [String: String]
        XCTAssertEqual(body?["password"]?.utf8.count, 72)
        do { _ = try await client.authenticate(email: "user@example.com", password: String(repeating: "密", count: 25), deviceID: UUID()); XCTFail("Expected byte limit") }
        catch AuthError.invalidResponse {}
    }

    func testSharedPasswordRulesDistinguishLoginFromNewPassword() {
        XCTAssertTrue(EmailPasswordRules.isValidLoginPassword("a"))
        XCTAssertFalse(EmailPasswordRules.isValidLoginPassword(""))
        XCTAssertFalse(EmailPasswordRules.isValidNewPassword(String(repeating: "a", count: 14)))
        XCTAssertTrue(EmailPasswordRules.isValidNewPassword(String(repeating: "密", count: 24)))
        XCTAssertFalse(EmailPasswordRules.isValidNewPassword(String(repeating: "密", count: 25)))
        XCTAssertTrue(EmailPasswordRules.isValidNewPassword(" password long "))
    }

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
    private func makeClient(response: String, status: Int = 200, languageProvider: (@MainActor @Sendable () -> String?)? = nil) throws -> (AppCloudAuthClient, RequestRecorder) {
        let recorder = RequestRecorder(response: Data(response.utf8), status: status)
        let config = URLSessionConfiguration.ephemeral
        config.protocolClasses = [StubURLProtocol.self]
        let identifier = UUID().uuidString
        StubURLProtocol.registry.insert(recorder, id: identifier)
        config.httpAdditionalHeaders = ["X-Test-ID": identifier]
        let session = URLSession(configuration: config)
        if let languageProvider {
            return (try AppCloudAuthClient(baseURL: URL(string: "https://example.com/adbox")!, session: session, languageProvider: languageProvider), recorder)
        }
        return (try AppCloudAuthClient(baseURL: URL(string: "https://example.com/adbox")!, session: session), recorder)
    }
}

/// 测试与客户端在主线程读写同一语言来源，模拟宿主设置切换。
@MainActor
private final class PreferredLanguageSource {
    var value: String?
    init(_ value: String?) { self.value = value }
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
