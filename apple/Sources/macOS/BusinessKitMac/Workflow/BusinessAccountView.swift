#if os(macOS)
import AuthCore
import DesignKitMac
import SwiftUI

/// 通过宿主的 AuthCore 会话显示账号状态。默认提供邮件登录，可接入宿主的登录或账号管理流程。
public struct BusinessAccountView: View {
    private let session: AuthSessionStore
    private let signIn: (@MainActor () async throws -> Void)?
    private let signOut: @MainActor () async throws -> Void
    private let manageAccount: (() -> Void)?
    @Environment(\.eControlTheme) private var theme
    @State private var showingEmail = false
    @State private var confirmingSignOut = false
    @State private var busy = false
    @State private var failure: LocalizedStringKey?

    /// 宿主创建并恢复会话，按产品决定账号管理入口。signIn 为空时使用邮件与密码登录。
    public init(
        session: AuthSessionStore,
        signIn: (@MainActor () async throws -> Void)? = nil,
        signOut: (@MainActor () async throws -> Void)? = nil,
        manageAccount: (() -> Void)? = nil
    ) {
        self.session = session
        self.signIn = signIn
        self.signOut = signOut ?? { try await session.signOut() }
        self.manageAccount = manageAccount
    }

    public var body: some View {
        VStack(alignment: .leading, spacing: theme.spacing.group) {
            EPageHeader(title: workflowText("account.title"))
            ECard {
                if busy || session.isSigningIn {
                    EContentState(.loading, title: workflowText("account.loading")) { EmptyView() }
                } else if let user = session.session?.user {
                    signedIn(user)
                } else {
                    EContentState(.empty, title: workflowText("account.signedOut"), systemImage: "person.crop.circle") {
                        EButton(emphasis: .primary, action: beginSignIn) { workflowText("account.signIn") }
                    }
                }
            }
            if let failure {
                EStatusBadge(workflowText(failure), tone: .failure)
            }
        }
        .sheet(isPresented: $showingEmail) {
            EmailSignInSheet(session: session).eControlTheme(theme)
        }
        .confirmationDialog(workflowText("account.signOutPrompt"), isPresented: $confirmingSignOut) {
            Button(role: .destructive) {
                perform(signOut, failure: "account.signOutFailed")
            } label: {
                workflowText("account.signOut")
            }
            Button(role: .cancel) {} label: { workflowText("common.cancel") }
        }
    }

    private func signedIn(_ user: AuthUser) -> some View {
        VStack(alignment: .leading, spacing: theme.spacing.controlGroup) {
            if let name = user.displayName, !name.isEmpty {
                Text(verbatim: name).font(theme.typography.sectionTitle)
            }
            if let email = user.email, !email.isEmpty {
                Text(verbatim: email).font(theme.typography.secondary)
            }
            EStatusBadge(workflowText("account.signedIn"), tone: .success)
            HStack(spacing: theme.spacing.controlGroup) {
                if let manageAccount {
                    EButton(action: manageAccount) { workflowText("account.manage") }
                }
                EButton(action: { confirmingSignOut = true }) { workflowText("account.signOut") }
            }
        }
    }

    private func beginSignIn() {
        if let signIn {
            perform(signIn, failure: "account.signInFailed")
        } else {
            failure = nil
            showingEmail = true
        }
    }

    private func perform(_ operation: @escaping @MainActor () async throws -> Void, failure failureKey: LocalizedStringKey) {
        guard !busy, !session.isSigningIn else { return }
        busy = true
        failure = nil
        Task {
            defer { busy = false }
            do {
                try await operation()
            } catch is CancellationError {
                return
            } catch {
                failure = failureKey
            }
        }
    }
}

private struct EmailSignInSheet: View {
    let session: AuthSessionStore
    @Environment(\.dismiss) private var dismiss
    @Environment(\.eControlTheme) private var theme
    @State private var email = ""
    @State private var password = ""
    @State private var busy = false
    @State private var failed = false

    var body: some View {
        VStack(alignment: .leading, spacing: theme.spacing.group) {
            EPageHeader(title: workflowText("account.signIn"))
            ETextField(workflowText("account.email"), text: $email)
                .textContentType(.emailAddress)
            ESecureField(workflowText("account.password"), text: $password)
                .textContentType(.password)
            if failed {
                EStatusBadge(workflowText("account.signInFailed"), tone: .failure)
            }
            HStack {
                Spacer()
                EButton(action: { dismiss() }) { workflowText("common.cancel") }
                    .keyboardShortcut(.cancelAction)
                EButton(emphasis: .primary, isBusy: busy, action: submit) {
                    workflowText("account.signIn")
                }
                .keyboardShortcut(.defaultAction)
                .disabled(email.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty || password.isEmpty)
            }
        }
        .padding(theme.spacing.pageInset)
        .frame(minWidth: 340)
        .disabled(busy || session.isSigningIn)
        .interactiveDismissDisabled(busy || session.isSigningIn)
    }

    private func submit() {
        guard !busy, !session.isSigningIn else { return }
        let accountEmail = email.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !accountEmail.isEmpty, !password.isEmpty else { return }
        busy = true
        failed = false
        Task {
            defer {
                busy = false
                password = ""
            }
            do {
                try await session.signIn(email: accountEmail, password: password)
                dismiss()
            } catch is CancellationError {
                return
            } catch {
                failed = true
            }
        }
    }
}
#endif
