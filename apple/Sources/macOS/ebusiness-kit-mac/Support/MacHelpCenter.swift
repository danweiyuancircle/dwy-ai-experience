#if os(macOS)
import AppKit
import DesignKitMac
import SwiftUI
import WebKit

/// 应用提供的 FAQ 或文档入口。ID 在同一帮助中心中须唯一。
public struct MacHelpTopic: Identifiable {
    public let id: String
    let title: Text
    let summary: Text?
    let documentURL: URL?

    /// 文档使用 HTTP 或 HTTPS，FAQ 正文在应用内直接显示。
    public init(id: String, title: Text, summary: Text? = nil, documentURL: URL? = nil) {
        self.id = id
        self.title = title
        self.summary = summary
        self.documentURL = documentURL
    }
}

/// 应用指定的反馈渠道。ID 在同一帮助中心中须唯一。
public struct MacFeedbackContact: Identifiable {
    /// 用户可以打开网页或邮件客户端，也可以复制群号等联系信息。
    public enum Action {
        case open(URL)
        case copy(String)
    }

    public let id: String
    let title: Text
    let detail: Text?
    let action: Action
    let systemImage: String?
    let accessibilityLabel: Text?
    let accessibilityHint: Text?

    /// `id` 同时用于辅助功能自动化标识。图标和辅助功能描述可由宿主传入。
    public init(
        id: String,
        title: Text,
        detail: Text? = nil,
        action: Action,
        systemImage: String? = nil,
        accessibilityLabel: Text? = nil,
        accessibilityHint: Text? = nil
    ) {
        self.id = id
        self.title = title
        self.detail = detail
        self.action = action
        self.systemImage = systemImage
        self.accessibilityLabel = accessibilityLabel
        self.accessibilityHint = accessibilityHint
    }
}

/// 应用内帮助与反馈，可以放在设置分类或原生 sheet 中。
public struct MacHelpCenter: View {
    @Environment(\.eControlTheme) private var theme
    private let title: Text
    private let topics: [MacHelpTopic]
    private let contacts: [MacFeedbackContact]
    private let onClose: (() -> Void)?

    /// 在独立 sheet 中传入宿主关闭动作，即可显示关闭按钮并支持 Escape。
    public init(
        title: Text,
        topics: [MacHelpTopic] = [],
        contacts: [MacFeedbackContact] = [],
        onClose: (() -> Void)? = nil
    ) {
        self.title = title
        self.topics = topics
        self.contacts = contacts
        self.onClose = onClose
    }

    public var body: some View {
        VStack(spacing: 0) {
            if let onClose {
                MacBusinessSheetHeader(title: title, onClose: onClose)
                Divider()
            }
            navigationContent
        }
        .background(theme.colors.background)
    }

    private var navigationContent: some View {
        NavigationStack {
            ESettingsPage(maxContentWidth: 680) {
                if onClose == nil { EPageHeader(title: title) }
                if !topics.isEmpty {
                    supportText("Help and documents").font(theme.typography.sectionTitle)
                    ECard {
                        VStack(alignment: .leading, spacing: theme.spacing.group) {
                            ForEach(topics) { topic in
                                if let url = topic.documentURL {
                                    NavigationLink {
                                        MacSupportDocument(title: topic.title, url: url)
                                    } label: {
                                        Label { topic.title } icon: { Image(systemName: "doc.text") }
                                    }
                                    if let summary = topic.summary {
                                        summary.font(theme.typography.secondary).foregroundStyle(theme.colors.secondaryText)
                                    }
                                } else if let summary = topic.summary {
                                    DisclosureGroup { summary.padding(.top, theme.spacing.inline) } label: { topic.title }
                                } else {
                                    topic.title
                                }
                            }
                        }
                    }
                }
                if !contacts.isEmpty {
                    supportText("Contact and feedback").font(theme.typography.sectionTitle)
                    ECard { MacFeedbackContacts(contacts: contacts) }
                }
            }
        }
    }
}

/// 仅呈现联系项，适用于现有帮助、设置分类和原生 popover。
public struct MacFeedbackContacts: View {
    @Environment(\.eControlTheme) private var theme
    @Environment(\.openURL) private var openURL
    @State private var copiedContact: String?
    @State private var copyFailedContact: String?
    @State private var openFailed = false
    private let contacts: [MacFeedbackContact]
    private let onOpen: (() -> Void)?

    /// `onOpen` 在系统接受链接后调用，复制操作保留在当前界面。
    public init(contacts: [MacFeedbackContact], onOpen: (() -> Void)? = nil) {
        self.contacts = contacts
        self.onOpen = onOpen
    }

    public var body: some View {
        VStack(alignment: .leading, spacing: theme.spacing.group) {
            ForEach(contacts) { contact in
                EButton(action: { perform(contact) }) {
                    HStack(spacing: theme.spacing.group) {
                        if let systemImage = contact.systemImage {
                            Image(systemName: systemImage).accessibilityHidden(true)
                        }
                        VStack(alignment: .leading, spacing: theme.spacing.inline) {
                            contact.title
                            if let detail = contact.detail {
                                detail.font(theme.typography.secondary).foregroundStyle(theme.colors.secondaryText)
                            }
                        }
                        Spacer()
                        if copiedContact == contact.id {
                            supportText("Copied").foregroundStyle(theme.colors.success)
                                .accessibilityHidden(true)
                        } else {
                            Image(systemName: contactIcon(contact.action)).accessibilityHidden(true)
                        }
                    }
                    .frame(maxWidth: .infinity, alignment: .leading)
                }
                .accessibilityLabel(contact.accessibilityLabel ?? Text(""), isEnabled: contact.accessibilityLabel != nil)
                .accessibilityHint(contact.accessibilityHint ?? Text(""), isEnabled: contact.accessibilityHint != nil)
                .accessibilityValue(supportText("Copied"), isEnabled: copiedContact == contact.id)
                .accessibilityIdentifier(contact.id)
                if copyFailedContact == contact.id, case .copy(let value) = contact.action {
                    VStack(alignment: .leading, spacing: theme.spacing.inline) {
                        supportText("Unable to copy. Copy this value manually:")
                        Text(verbatim: value).textSelection(.enabled)
                    }
                    .font(theme.typography.secondary)
                    .accessibilityAddTraits(.updatesFrequently)
                }
            }
        }
        .alert(isPresented: $openFailed) {
            Alert(title: supportText("Unable to use this contact"), dismissButton: .default(supportText("OK")))
        }
    }

    private func perform(_ contact: MacFeedbackContact) {
        copiedContact = nil
        copyFailedContact = nil
        switch contact.action {
        case .open(let url):
            guard SupportLink.canOpen(url) else {
                openFailed = true
                return
            }
            openURL(url) { accepted in
                if accepted { onOpen?() }
                else { openFailed = true }
            }
        case .copy(let value):
            NSPasteboard.general.clearContents()
            if NSPasteboard.general.setString(value, forType: .string) {
                copiedContact = contact.id
            } else {
                copyFailedContact = contact.id
            }
        }
    }

    private func contactIcon(_ action: MacFeedbackContact.Action) -> String {
        switch action {
        case .open: "arrow.up.right.square"
        case .copy: "document.on.document"
        }
    }
}

enum SupportLink {
    static func canRead(_ url: URL) -> Bool {
        guard let scheme = url.scheme?.lowercased(), ["https", "http"].contains(scheme) else { return false }
        return url.host?.isEmpty == false
    }

    static func canOpen(_ url: URL) -> Bool {
        canRead(url) || (url.scheme?.lowercased() == "mailto" && !url.path.isEmpty)
    }
}

private struct MacSupportDocument: View {
    @State private var reader = MacSupportDocumentReader()
    private let title: Text
    private let url: URL

    init(title: Text, url: URL) {
        self.title = title
        self.url = url
    }

    var body: some View {
        MacSupportWebView(webView: reader.webView)
            .opacity(reader.status == .ready ? 1 : 0)
            .accessibilityHidden(reader.status != .ready)
            .overlay {
                switch reader.status {
                case .loading:
                    ProgressView { supportText("Loading document") }
                case .failed:
                    VStack(spacing: 12) {
                        Label { supportText("Unable to load document") } icon: { Image(systemName: "wifi.exclamationmark") }
                        EButton { reader.load(url) } label: { supportText("Retry") }
                    }
                case .ready:
                    EmptyView()
                }
            }
            .navigationTitle(title)
            .task(id: url) { reader.load(url) }
    }
}

private struct MacSupportWebView: NSViewRepresentable {
    let webView: WKWebView

    func makeNSView(context: Context) -> WKWebView { webView }
    func updateNSView(_ nsView: WKWebView, context: Context) {}
}

@MainActor
@Observable
private final class MacSupportDocumentReader: NSObject, WKNavigationDelegate {
    enum Status { case loading, ready, failed }

    let webView: WKWebView
    private(set) var status = Status.loading
    private var documentURL: URL?
    private var currentNavigation: WKNavigation?

    override init() {
        let configuration = WKWebViewConfiguration()
        configuration.websiteDataStore = .nonPersistent()
        webView = WKWebView(frame: .zero, configuration: configuration)
        super.init()
        webView.navigationDelegate = self
        webView.allowsBackForwardNavigationGestures = true
    }

    func load(_ url: URL) {
        documentURL = url
        guard SupportLink.canRead(url) else {
            status = .failed
            return
        }
        status = .loading
        currentNavigation = webView.load(URLRequest(url: url))
        if currentNavigation == nil { status = .failed }
    }

    func webView(_ webView: WKWebView, didStartProvisionalNavigation navigation: WKNavigation!) {
        currentNavigation = navigation
        status = .loading
    }

    func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
        if currentNavigation === navigation { status = .ready }
    }

    func webView(_ webView: WKWebView, didFail navigation: WKNavigation!, withError error: Error) {
        if currentNavigation === navigation { status = .failed }
    }

    func webView(_ webView: WKWebView, didFailProvisionalNavigation navigation: WKNavigation!, withError error: Error) {
        if currentNavigation === navigation { status = .failed }
    }

    func webViewWebContentProcessDidTerminate(_ webView: WKWebView) {
        status = .failed
    }

    func webView(_ webView: WKWebView, decidePolicyFor navigationResponse: WKNavigationResponse) async -> WKNavigationResponsePolicy {
        if navigationResponse.isForMainFrame,
           let response = navigationResponse.response as? HTTPURLResponse,
           response.statusCode >= 400 {
            status = .failed
            return .cancel
        }
        return .allow
    }

    func webView(_ webView: WKWebView, decidePolicyFor action: WKNavigationAction) async -> WKNavigationActionPolicy {
        guard let url = action.request.url else { return .cancel }
        if action.navigationType == .linkActivated,
           (url.host != documentURL?.host || url.scheme?.lowercased() == "mailto"),
           SupportLink.canOpen(url) {
            NSWorkspace.shared.open(url)
            return .cancel
        }
        guard SupportLink.canRead(url) else { return .cancel }
        if action.targetFrame == nil {
            if action.navigationType == .linkActivated { webView.load(action.request) }
            return .cancel
        }
        return .allow
    }
}

func supportText(_ key: LocalizedStringKey) -> Text {
    Text(key, tableName: "Support", bundle: .module)
}
#endif
