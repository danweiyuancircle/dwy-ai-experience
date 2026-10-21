#if os(iOS)
import SwiftUI
import AuthCore

/// 宿主提供品牌标题和法律链接；主题颜色沿用 SwiftUI 的 tint。
public struct AuthUIConfiguration: Sendable {
    public let appName: String
    public let termsURL: URL?
    public let privacyPolicyURL: URL?

    public init(appName: String, termsURL: URL? = nil, privacyPolicyURL: URL? = nil) {
        self.appName = appName
        self.termsURL = termsURL
        self.privacyPolicyURL = privacyPolicyURL
    }
}

/// 完整的邮箱登录、验证码注册和密码重置流程。宿主在完成回调中关闭页面。
/// 注册/登录只通过传入会话管理器安装凭据；退出视图会失效未完成的认证操作。
@MainActor
public struct AuthFlowView: View {
    @State private var model: AuthFlowModel
    @State private var showsPassword = false
    @Environment(\.locale) private var locale
    @FocusState private var focusedField: Field?
    private let configuration: AuthUIConfiguration
    private let onAuthenticated: (AuthUser) -> Void
    private let onCancel: (() -> Void)?

    private enum Field: Hashable { case email, password, code }

    public init(
        session: AuthSessionStore,
        configuration: AuthUIConfiguration,
        onAuthenticated: @escaping (AuthUser) -> Void,
        onCancel: (() -> Void)? = nil
    ) {
        _model = State(initialValue: AuthFlowModel(actions: AuthFlowActions(session: session)))
        self.configuration = configuration
        self.onAuthenticated = onAuthenticated
        self.onCancel = onCancel
    }

    public var body: some View {
        @Bindable var model = model
        NavigationStack {
            Form {
                Section {
                    Text(copy(subtitleKey))
                        .foregroundStyle(.secondary)
                        .listRowBackground(Color.clear)
                }
                Section {
                    TextField(copy("email"), text: $model.email)
                        .keyboardType(.emailAddress)
                        .textContentType(.username)
                        .textInputAutocapitalization(.never)
                        .autocorrectionDisabled()
                        .focused($focusedField, equals: .email)
                        .submitLabel(.next)
                        .onSubmit { focusedField = .password }
                        .accessibilityIdentifier("auth.email")
                        .onChange(of: model.email) { _, value in
                            if value.utf8.count > 320 { model.email = String(value.prefix(320)) }
                        }
                    passwordField
                    if model.mode != .login {
                        TextField(copy("code"), text: $model.code)
                            .keyboardType(.numberPad)
                            .textContentType(.oneTimeCode)
                            .focused($focusedField, equals: .code)
                            .accessibilityIdentifier("auth.code")
                            .onChange(of: model.code) { _, value in
                                let filtered = String(value.filter { $0.isASCII && $0.isNumber }.prefix(model.challenge?.codeLength ?? 6))
                                if filtered != value { model.code = filtered }
                            }
                        TimelineView(.periodic(from: .now, by: 1)) { context in
                            let seconds = model.resendSeconds(at: context.date)
                            Button(seconds > 0 ? String(format: copy("resendIn"), seconds) : copy("sendCode")) {
                                focusedField = nil
                                Task { await model.sendCode() }
                            }
                            .disabled(model.isBusy || seconds > 0)
                            .accessibilityIdentifier("auth.sendCode")
                        }
                    }
                } footer: {
                    if model.mode != .login { Text(copy("passwordHint")) }
                }
                .disabled(model.isBusy)
                if let message = model.message {
                    Section {
                        Text(copy(message.rawValue))
                            .foregroundStyle(model.isNotice ? Color.secondary : Color.red)
                            .accessibilityIdentifier("auth.message")
                    }
                }
                Section {
                    Button {
                        focusedField = nil
                        Task {
                            if let user = await model.submit() { onAuthenticated(user) }
                        }
                    } label: {
                        HStack {
                            if model.isBusy { ProgressView().accessibilityLabel(copy("working")) }
                            Text(copy(actionKey))
                        }
                        .frame(maxWidth: .infinity)
                    }
                    .buttonStyle(.borderedProminent)
                    .controlSize(.large)
                    .disabled(model.isBusy)
                    .accessibilityIdentifier("auth.submit")
                    if model.mode == .login {
                        Button(copy("register")) { switchMode(.register) }
                            .accessibilityIdentifier("auth.goRegister")
                        Button(copy("forgotPassword")) { switchMode(.resetPassword) }
                            .accessibilityIdentifier("auth.goReset")
                    } else {
                        Button(copy("backToLogin")) { switchMode(.login) }
                            .accessibilityIdentifier("auth.goLogin")
                    }
                }
                .disabled(model.isBusy)
                if configuration.termsURL != nil || configuration.privacyPolicyURL != nil {
                    Section {
                        Text(copy("legalNotice")).font(.footnote).foregroundStyle(.secondary)
                        if let url = configuration.termsURL { Link(copy("terms"), destination: url) }
                        if let url = configuration.privacyPolicyURL { Link(copy("privacy"), destination: url) }
                    }
                }
            }
            .scrollDismissesKeyboard(.interactively)
            .background(Color(uiColor: .systemGroupedBackground).onTapGesture { focusedField = nil })
            .navigationTitle(configuration.appName)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                if let onCancel {
                    ToolbarItem(placement: .cancellationAction) {
                        Button(copy("cancel")) { model.cancel(); onCancel() }
                    }
                }
                ToolbarItemGroup(placement: .keyboard) {
                    Spacer()
                    Button(copy("done")) { focusedField = nil }
                }
            }
        }
        .onDisappear { model.cancel() }
    }

    private var passwordField: some View {
        @Bindable var model = model
        return HStack {
            Group {
                if showsPassword { TextField(copy(model.mode == .resetPassword ? "newPassword" : "password"), text: $model.password) }
                else { SecureField(copy(model.mode == .resetPassword ? "newPassword" : "password"), text: $model.password) }
            }
            .textContentType(model.mode == .login ? .password : .newPassword)
            .textInputAutocapitalization(.never)
            .autocorrectionDisabled()
            .focused($focusedField, equals: .password)
            .submitLabel(model.mode == .login ? .go : .next)
            .accessibilityIdentifier("auth.password")
            .onSubmit {
                if model.mode == .login {
                    focusedField = nil
                    Task { if let user = await model.submit() { onAuthenticated(user) } }
                } else { focusedField = .code }
            }
            Button {
                showsPassword.toggle()
            } label: {
                Image(systemName: showsPassword ? "eye.slash" : "eye")
            }
            .buttonStyle(.borderless)
            .accessibilityLabel(copy(showsPassword ? "hidePassword" : "showPassword"))
        }
    }

    private var subtitleKey: String {
        switch model.mode {
        case .login: "loginSubtitle"
        case .register: "registerSubtitle"
        case .resetPassword: "resetSubtitle"
        }
    }

    private var actionKey: String {
        switch model.mode {
        case .login: "login"
        case .register: "registerAction"
        case .resetPassword: "resetAction"
        }
    }

    private func switchMode(_ mode: AuthFlowMode) {
        focusedField = nil
        showsPassword = false
        model.switchMode(mode)
    }

    private func copy(_ key: String) -> String { AuthStrings.text(key, locale: locale) }
}
#endif
