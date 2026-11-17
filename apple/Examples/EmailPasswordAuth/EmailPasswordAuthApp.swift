import SwiftUI
import AuthCore
import AuthUI

/// 示例宿主：替换 AppConfig.authBaseURL 后即可接入真实应用后端。
@main
@MainActor
struct EmailPasswordAuthApp: App {
    @State private var session: AuthSessionStore
    @State private var initializationError = false
    @State private var showsAuth = false
    @State private var operationError = false
    @Environment(\.scenePhase) private var scenePhase

    init() {
        do {
            let client = try AppCloudAuthClient(baseURL: AppConfig.authBaseURL)
            let tokenStore = try KeychainRefreshTokenStore(namespace: AppConfig.namespace, backendURL: AppConfig.authBaseURL)
            let deviceID = try AuthDeviceIdentity.loadOrCreate(namespace: AppConfig.namespace)
            _session = State(initialValue: AuthSessionStore(backend: client, tokenStore: tokenStore, deviceID: deviceID))
        } catch {
            // 示例中的固定配置应可构造；错误必须显式暴露，不能使用假登录替代。
            preconditionFailure("Invalid authentication configuration")
        }
    }

    var body: some Scene {
        WindowGroup {
            Group {
                if let user = session.session?.user {
                    NavigationStack {
                        List {
                            LabeledContent("Email", value: user.email ?? "")
                            Button("Sign out") {
                                Task {
                                    do { try await session.signOut() }
                                    catch { operationError = true }
                                    showsAuth = true
                                }
                            }
                        }
                        .navigationTitle("AuthUI Example")
                    }
                } else {
                    ContentUnavailableView {
                        Label("Sign in to continue", systemImage: "person.crop.circle")
                    } description: {
                        if initializationError { Text("Could not restore your session. Check the backend and network, then sign in.") }
                    }
                        .safeAreaInset(edge: .bottom) {
                            Button("Sign in") { showsAuth = true }.buttonStyle(.borderedProminent).padding()
                        }
                }
            }
            .sheet(isPresented: $showsAuth) {
                AuthFlowView(
                    session: session,
                    configuration: AuthUIConfiguration(appName: "AuthUI Example"),
                    onAuthenticated: { _ in showsAuth = false },
                    onCancel: { showsAuth = false }
                )
                .environment(\.locale, Locale(identifier: "zh-Hans"))
            }
            .task {
                do {
                    try await session.restore()
                } catch {
                    // 网络暂时失败不删除 Keychain；保留后续恢复机会。
                    initializationError = true
                }
                showsAuth = session.session == nil
            }
            .onChange(of: scenePhase) { _, phase in
                guard phase == .active, session.session != nil, !showsAuth else { return }
                Task {
                    do { try await session.refreshIfNeeded() }
                    catch { operationError = true }
                }
            }
            .alert("Request failed", isPresented: $operationError) {
                Button("OK", role: .cancel) {}
            }
        }
    }
}

/// 可调参数只在宿主集中声明；不同产品使用不同 namespace 和后端前缀。
private enum AppConfig {
    static let authBaseURL = URL(string: "https://api.example.com/adbox")!
    static let namespace = "com.dwy.auth-example"
}
