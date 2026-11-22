import AuthCore
import Foundation

@MainActor
func makeGalleryAccount() -> AuthSessionStore {
    AuthSessionStore(
        backend: GalleryAuthBackend(),
        provider: GallerySignIn(),
        tokenStore: GalleryTokenStore(),
        deviceID: UUID()
    )
}

private struct GalleryAuthBackend: AuthBackend {
    private let user = AuthUser(id: UUID(), email: "demo@example.invalid", displayName: "Demo Account")

    func authenticate(googleIDToken: String, deviceID: UUID) async throws -> AuthTokenResponse {
        response()
    }

    func refresh(refreshToken: String) async throws -> AuthTokenResponse {
        response()
    }

    func logout(accessToken: String) async throws {}

    private func response() -> AuthTokenResponse {
        AuthTokenResponse(accessToken: UUID().uuidString, refreshToken: UUID().uuidString, expiresIn: 3600, user: user)
    }
}

private struct GallerySignIn: GoogleIDTokenProviding {
    func signIn() async throws -> String { "local-preview" }
    func signOut() {}
}

private final class GalleryTokenStore: RefreshTokenStoring {
    private var value: String?

    func load() throws -> String? { value }
    func save(_ token: String) throws { value = token }
    func delete() throws { value = nil }
}
