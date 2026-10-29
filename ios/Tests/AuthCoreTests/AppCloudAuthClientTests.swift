import XCTest
@testable import AuthCore

/// URLProtocol 捕获真实 URLSession 请求，验证应用前缀和 eapi 契约。
@MainActor
final class AppCloudAuthClientTests: XCTestCase {

    func testAppleReauthenticationChallengeIsAuthorizedAndCredentialKeepsCode() async throws {
        let (client, recorder) = try makeClient(response: """
        {"code":"SUCCESS","message":"ok","data":{"challenge_id":"challenge","nonce":"server-nonce","expires_in":300}}
        """)
        _ = try await client.createAppleChallenge(purpose: .emailUpdate, accessToken: "current-access")
        XCTAssertEqual(recorder.request?.value(forHTTPHeaderField: "Authorization"), "Bearer current-access")
        let body = try XCTUnwrap(JSONSerialization.jsonObject(with: recorder.body) as? [String: String])
        XCTAssertEqual(body, ["purpose": "reauth_email_update"])
        let proof = AuthReauthentication.apple(authorization: AppleAuthorization(identityToken: "apple-token", authorizationCode: "apple-code"), challengeID: "challenge")
        let encoded = try XCTUnwrap(JSONSerialization.jsonObject(with: JSONEncoder().encode(proof)) as? [String: String])
        XCTAssertEqual(encoded["method"], "external")
        XCTAssertEqual(encoded["identifier"], "apple")
        let credential = try XCTUnwrap(encoded["credential"]?.data(using: .utf8))
        let fields = try XCTUnwrap(JSONSerialization.jsonObject(with: credential) as? [String: String])
        XCTAssertEqual(fields, ["challenge_id": "challenge", "identity_token": "apple-token", "authorization_code": "apple-code"])
    }
    func testAppleChallengePreservesPrefixAndDecodesRawNonce() async throws {
        let (client, recorder) = try makeClient(response: """
        {"code":"SUCCESS","message":"ok","data":{"challenge_id":"apple-challenge","nonce":"raw_nonce-123","expires_in":300}}
        """)
        let challenge = try await client.createAppleChallenge()
        XCTAssertEqual(recorder.request?.url?.absoluteString, "https://example.com/adbox/api/v1/auth/apple/challenges")
        XCTAssertEqual(recorder.request?.httpMethod, "POST")
        XCTAssertNil(recorder.request?.value(forHTTPHeaderField: "Authorization"))
        XCTAssertTrue(recorder.body.isEmpty || recorder.body == Data("{}".utf8))
        XCTAssertEqual(challenge.challengeID, "apple-challenge")
        XCTAssertEqual(challenge.nonce, "raw_nonce-123")
        XCTAssertEqual(challenge.expiresIn, 300)
    }

    func testAppleExchangeEncodesOnlyContractFieldsAndOptionalName() async throws {
        let deviceID = UUID()
        let userID = UUID()
        for name: String? in [nil, "Apple Name"] {
            let (client, recorder) = try makeClient(response: """
            {"code":"SUCCESS","message":"ok","data":{"access_token":"access","refresh_token":"refresh","token_type":"Bearer","expires_in":900,"user":{"id":"\(userID)","email":null,"display_name":"Backend Name"}}}
            """)
            let authorization = AppleAuthorization(identityToken: "apple-token", authorizationCode: "apple-code", displayName: name)
            let result = try await client.authenticate(appleAuthorization: authorization, challengeID: "challenge", deviceID: deviceID)
            XCTAssertEqual(recorder.request?.url?.path, "/adbox/api/v1/auth/apple")
            XCTAssertEqual(recorder.request?.httpMethod, "POST")
            let body = try XCTUnwrap(JSONSerialization.jsonObject(with: recorder.body) as? [String: String])
            var expected = ["challenge_id": "challenge", "identity_token": "apple-token", "authorization_code": "apple-code", "device_id": deviceID.uuidString]
            expected["display_name"] = name
            XCTAssertEqual(body, expected)
            XCTAssertEqual(result.user.id, userID)
            XCTAssertEqual(result.user.displayName, "Backend Name")
            XCTAssertEqual(result.refreshToken, "refresh")
        }
    }

    func testAppleChallengeRejectsMalformedPayloadsAndServerFailures() async throws {
        for payload in ["null", "{}", "{\"challenge_id\":\"\",\"nonce\":\"raw\",\"expires_in\":300}", "{\"challenge_id\":\"id\",\"nonce\":\"\",\"expires_in\":300}", "{\"challenge_id\":\"id\",\"nonce\":\"raw\",\"expires_in\":0}"] {
            let (client, _) = try makeClient(response: "{\"code\":\"SUCCESS\",\"message\":\"ok\",\"data\":\(payload)}")
            do { _ = try await client.createAppleChallenge(); XCTFail("Expected invalid challenge") }
            catch AuthError.invalidResponse {}
        }
        for status in [200, 401] {
            let (client, _) = try makeClient(response: "{\"code\":\"APPLE_AUTH_FAILED\",\"message\":\"invalid\",\"data\":null}", status: status)
            do { _ = try await client.createAppleChallenge(); XCTFail("Expected server failure") }
            catch AuthError.server(let code, _) { XCTAssertEqual(code, "APPLE_AUTH_FAILED") }
        }
    }

    func testAppleExchangeRejectsInvalidInputBeforeNetworkAndPropagatesFailure() async throws {
        let (client, recorder) = try makeClient(response: "{\"code\":\"APPLE_AUTH_FAILED\",\"message\":\"invalid\",\"data\":null}", status: 401)
        let invalid = [
            AppleAuthorization(identityToken: "", authorizationCode: "code"),
            AppleAuthorization(identityToken: "token", authorizationCode: ""),
            AppleAuthorization(identityToken: String(repeating: "x", count: 16_385), authorizationCode: "code"),
            AppleAuthorization(identityToken: "token", authorizationCode: String(repeating: "x", count: 4_097)),
            AppleAuthorization(identityToken: "token", authorizationCode: "code", displayName: String(repeating: "名", count: 256)),
        ]
        for authorization in invalid {
            do { _ = try await client.authenticate(appleAuthorization: authorization, challengeID: "id", deviceID: UUID()); XCTFail("Expected invalid input") }
            catch AuthError.invalidResponse {}
        }
        XCTAssertNil(recorder.request)
        do { _ = try await client.authenticate(appleAuthorization: AppleAuthorization(identityToken: "token", authorizationCode: "code"), challengeID: "id", deviceID: UUID()); XCTFail("Expected Apple rejection") }
        catch AuthError.server(let code, _) { XCTAssertEqual(code, "APPLE_AUTH_FAILED") }
    }

    /// 同一 HTTP 客户端不能复用上一次登录的购买证明，包括自动恢复会话。
    func testSameClientReadsFreshProofAgainForRefresh() async throws {
        var reads = 0
        let (client, recorder) = try makeClient(response: """
        {"code":"SUCCESS","message":"ok","data":{"access_token":"access","refresh_token":"refresh","token_type":"Bearer","expires_in":900,"user":{"id":"\(UUID())","email":null,"display_name":null}}}
        """, admissionProofProvider: { reads += 1; return "proof-\(reads)" })
        _ = try await client.authenticate(googleIDToken: "id-token", deviceID: UUID())
        let identifier = try XCTUnwrap(recorder.request?.value(forHTTPHeaderField: "X-Test-ID"))
        StubURLProtocol.registry.insert(recorder, id: identifier)
        _ = try await client.refresh(refreshToken: "refresh")
        let body = try XCTUnwrap(JSONSerialization.jsonObject(with: recorder.body) as? [String: String])
        XCTAssertEqual(reads, 2)
        XCTAssertEqual(body["admission_proof"], "proof-2")
    }

    /// 业务准入证明必须每次重新读取，覆盖所有会话入口；普通项目仍省略该字段。
    func testAdmissionProofIsIncludedForEverySessionExchange() async throws {
        for path in ["login", "register", "google", "external/login", "apple", "refresh", "email/update"] {
            var reads = 0
            let (client, recorder) = try makeClient(response: """
            {"code":"SUCCESS","message":"ok","data":{"access_token":"access","refresh_token":"refresh","token_type":"Bearer","expires_in":900,"user":{"id":"\(UUID())","email":null,"display_name":null}}}
            """, admissionProofProvider: { reads += 1; return "signed-proof-\(reads)" })
            switch path {
            case "login": _ = try await client.authenticate(email: "user@example.com", password: "password", deviceID: UUID())
            case "register": _ = try await client.register(email: "user@example.com", password: "long secure password", code: "012345", challengeID: "challenge", deviceID: UUID())
            case "google": _ = try await client.authenticate(googleIDToken: "id-token", deviceID: UUID())
            case "external/login": _ = try await client.authenticate(provider: "apple", credential: "apple-credential", deviceID: UUID())
            case "apple": _ = try await client.authenticate(appleAuthorization: AppleAuthorization(identityToken: "token", authorizationCode: "code"), challengeID: "challenge", deviceID: UUID())
            case "email/update": _ = try await client.updateEmail(email: "user@example.com", code: "012345", challengeID: UUID().uuidString, newPassword: nil, accessToken: "access")
            default: _ = try await client.refresh(refreshToken: "refresh")
            }
            XCTAssertEqual(reads, 1)
            XCTAssertEqual(recorder.request?.url?.path, "/adbox/api/v1/auth/\(path)")
            let body = try XCTUnwrap(JSONSerialization.jsonObject(with: recorder.body) as? [String: String])
            XCTAssertEqual(body["admission_proof"], "signed-proof-1")
        }
    }

    /// 缺购买、证明读取失败或超过边界时不能先发送凭据、取得临时会话。
    func testRejectedAdmissionProofNeverSendsCredentials() async throws {
        for proof in ["", String(repeating: "x", count: 131_073)] {
            let (client, recorder) = try makeClient(response: "{}", admissionProofProvider: { proof })
            do { _ = try await client.authenticate(email: "user@example.com", password: "password", deviceID: UUID()); XCTFail("Expected proof rejection") }
            catch AuthError.invalidResponse {}
            XCTAssertNil(recorder.request)
        }
        let (client, recorder) = try makeClient(response: "{}", admissionProofProvider: { throw AuthError.server(code: "PURCHASE_REQUIRED", message: "private") })
        do { _ = try await client.refresh(refreshToken: "refresh"); XCTFail("Expected proof source failure") }
        catch AuthError.server(let code, _) { XCTAssertEqual(code, "PURCHASE_REQUIRED") }
        XCTAssertNil(recorder.request)
    }
    /// 当前会话与强类型重新认证共同发码，不把 Google 当作 method 字段。
    func testEmailUpdateChallengeUsesBearerAndExternalReauthentication() async throws {
        let (client, recorder) = try makeClient(response: """
        {"code":"SUCCESS","message":"ok","data":{"challenge_id":"challenge","expires_in":300,"resend_after":60,"code_length":6}}
        """)
        let result = try await client.sendEmailUpdateCode(email: " UPDATED@Example.com ", reauthentication: .external(provider: "google", credential: "id-token"), accessToken: "current-access")
        XCTAssertEqual(result.challengeID, "challenge")
        XCTAssertEqual(recorder.request?.url?.path, "/adbox/api/v1/auth/email/update/code")
        XCTAssertEqual(recorder.request?.value(forHTTPHeaderField: "Authorization"), "Bearer current-access")
        let body = try XCTUnwrap(JSONSerialization.jsonObject(with: recorder.body) as? [String: Any])
        XCTAssertEqual(body["email"] as? String, "updated@example.com")
        XCTAssertEqual(body["reauthentication"] as? [String: String], ["method": "external", "identifier": "google", "credential": "id-token"])
    }

    /// 改邮箱只提交白名单字段，返回会话沿用原 token 信封。
    func testEmailUpdateDecodesRotatedSessionAndOmitsAbsentPassword() async throws {
        let (client, recorder) = try makeClient(response: """
        {"code":"SUCCESS","message":"ok","data":{"access_token":"rotated-access","refresh_token":"rotated-refresh","token_type":"Bearer","expires_in":900,"user":{"id":"\(UUID())","email":"updated@example.com","display_name":null}}}
        """)
        let response = try await client.updateEmail(email: "updated@example.com", code: "012345", challengeID: "00000000-0000-0000-0000-000000000001", newPassword: nil, accessToken: "current-access")
        XCTAssertEqual(response.refreshToken, "rotated-refresh")
        XCTAssertEqual(recorder.request?.url?.path, "/adbox/api/v1/auth/email/update")
        XCTAssertEqual(recorder.request?.value(forHTTPHeaderField: "Authorization"), "Bearer current-access")
        let body = try XCTUnwrap(JSONSerialization.jsonObject(with: recorder.body) as? [String: String])
        XCTAssertEqual(body, ["email": "updated@example.com", "code": "012345", "challenge_id": "00000000-0000-0000-0000-000000000001"])
    }

    /// 身份管理使用现有路由和重新认证，外部身份定位不泄露 token。
    func testIdentityListBindingAndUnlinkContracts() async throws {
        let (listing, listingRecorder) = try makeClient(response: """
        {"code":"SUCCESS","message":"ok","data":[{"kind":"external","value":"provider-subject","provider":"google","issuer":"https://accounts.google.com"}]}
        """)
        let identities = try await listing.listIdentities(accessToken: "current-access")
        XCTAssertEqual(listingRecorder.request?.httpMethod, "GET")
        XCTAssertEqual(listingRecorder.request?.url?.path, "/adbox/api/v1/auth/identities")
        let identity = try XCTUnwrap(identities.first)
        let (binding, bindRecorder) = try makeClient(response: """
        {"code":"SUCCESS","message":"ok","data":{"status":"completed"}}
        """)
        try await binding.bindExternal(provider: "google", credential: "new-id-token", reauthentication: .email(identifier: "user@example.com", password: "password"), accessToken: "current-access")
        XCTAssertEqual(bindRecorder.request?.url?.path, "/adbox/api/v1/auth/external/bind")
        let body = try XCTUnwrap(JSONSerialization.jsonObject(with: bindRecorder.body) as? [String: Any])
        XCTAssertEqual(Set(body.keys), ["provider", "credential", "reauthentication"])
        let (unlinking, unlinkRecorder) = try makeClient(response: """
        {"code":"SUCCESS","message":"ok","data":{"status":"completed"}}
        """)
        try await unlinking.unlinkIdentity(identity, reauthentication: .email(identifier: "user@example.com", password: "password"), accessToken: "current-access")
        XCTAssertEqual(unlinkRecorder.request?.url?.path, "/adbox/api/v1/auth/identity/unlink")
        let unlinkBody = try XCTUnwrap(JSONSerialization.jsonObject(with: unlinkRecorder.body) as? [String: Any])
        XCTAssertEqual(unlinkBody["provider"] as? String, "google")
        XCTAssertEqual(unlinkBody["issuer"] as? String, "https://accounts.google.com")
        XCTAssertEqual(unlinkBody["value"] as? String, "provider-subject")
    }

    /// 更新邮箱字段采用服务端 UUID 与密码政策，非法输入不能发网络请求。
    func testEmailUpdateRejectsMalformedChallengeAndWeakPasswordBeforeSending() async throws {
        let (client, recorder) = try makeClient(response: "{\"code\":\"SUCCESS\",\"message\":\"ok\",\"data\":null}")
        for (challenge, password) in [("not-a-uuid", Optional<String>.none), (UUID().uuidString, "short")] {
            do {
                _ = try await client.updateEmail(email: "u@example.com", code: "012345", challengeID: challenge, newPassword: password, accessToken: "access")
                XCTFail("Expected local rejection")
            } catch AuthError.invalidResponse {}
        }
        XCTAssertNil(recorder.request)
    }

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
    private func makeClient(response: String, status: Int = 200, languageProvider: (@MainActor @Sendable () -> String?)? = nil, admissionProofProvider: (@MainActor @Sendable () async throws -> String)? = nil) throws -> (AppCloudAuthClient, RequestRecorder) {
        let recorder = RequestRecorder(response: Data(response.utf8), status: status)
        let config = URLSessionConfiguration.ephemeral
        config.protocolClasses = [StubURLProtocol.self]
        let identifier = UUID().uuidString
        StubURLProtocol.registry.insert(recorder, id: identifier)
        config.httpAdditionalHeaders = ["X-Test-ID": identifier]
        let session = URLSession(configuration: config)
        if let languageProvider {
            return (try AppCloudAuthClient(baseURL: URL(string: "https://example.com/adbox")!, session: session, languageProvider: languageProvider, admissionProofProvider: admissionProofProvider), recorder)
        }
        return (try AppCloudAuthClient(baseURL: URL(string: "https://example.com/adbox")!, session: session, admissionProofProvider: admissionProofProvider), recorder)
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
