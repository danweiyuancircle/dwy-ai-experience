import SwiftUI
import StoreKit
import DesignCore
import DesignKitMac
import L10nKit
import LogKit
import PurchaseCore
import BizFoundation
import AppKit

// MARK: - ② Features / Settings
// 语言 / 外观本页下拉，不进子页。有付费必须挂 DEBUG 解锁。

struct SettingsView: View {
    @Environment(ThemeManager.self) private var theme
    @Environment(LocalizationManager.self) private var localization
    @Environment(LifetimeStore.self) private var store
    @Environment(\.requestReview) private var requestReview
    @Environment(\.openURL) private var openURL

    @State private var exportError: String?
    @State private var isExporting = false
    @State private var showPaywall = false

    var body: some View {
        @Bindable var theme = theme
        @Bindable var store = store
        let _ = localization.language
        List {
            Section {
                Button {
                    showPaywall = true
                } label: {
                    HStack {
                        Label(
                            store.isPurchased ? loc("settings_unlock_owned") : loc("settings_unlock_action"),
                            systemImage: store.isPurchased ? "checkmark.seal.fill" : "lock.fill"
                        )
                        Spacer()
                        if !store.isPurchased, let price = store.priceText {
                            Text(price)
                                .foregroundStyle(.secondary)
                        }
                    }
                }
                #if DEBUG
                Toggle(loc("settings_debug_unlock"), isOn: $store.debugUnlockAll)
                #endif
            } header: {
                Text(loc("settings_section_unlock"))
            } footer: {
                Text(loc("settings_unlock_hint"))
            }

            Section {
                LanguagePickerView()
                ThemePickerView(mode: $theme.mode)
            }

            Section {
                LabeledContent(loc("settings_version")) {
                    Text(versionText)
                        .foregroundStyle(.secondary)
                }
                Button {
                    if let url = AppConfig.privacyURL(localeIdentifier: localization.locale.identifier) {
                        openURL(url)
                    }
                } label: {
                    Label(loc("settings_privacy"), systemImage: "hand.raised")
                }
                Button {
                    sendFeedback()
                } label: {
                    Label(loc("settings_feedback"), systemImage: "envelope")
                }
                Button {
                    requestReview()
                    if let url = AppConfig.writeReviewURL {
                        openURL(url)
                    }
                } label: {
                    Label(loc("settings_rate"), systemImage: "star.bubble")
                }
            } header: {
                Text(loc("settings_section_about"))
            } footer: {
                Text(loc("settings_rate_footer"))
            }

            Section {
                Button {
                    exportLogs()
                } label: {
                    HStack {
                        Label(loc("settings_export_logs"), systemImage: "square.and.arrow.up")
                        Spacer()
                        if isExporting {
                            ProgressView()
                                .controlSize(.small)
                        }
                    }
                }
                .disabled(isExporting)
            } footer: {
                Text(loc("settings_export_logs_footer"))
            }
        }
        .navigationTitle(loc("settings_title"))
        .onAppear { store.startIfNeeded() }
        .sheet(isPresented: $showPaywall) {
            PaywallView()
                .environment(store)
                .environment(localization)
                .environment(theme)
        }
        .alert(loc("settings_export_logs_failed"), isPresented: Binding(
            get: { exportError != nil },
            set: { if !$0 { exportError = nil } }
        )) {
            Button(loc("common_ok"), role: .cancel) {}
        } message: {
            Text(exportError ?? "")
        }
    }

    private var versionText: String {
        let info = Bundle.main.infoDictionary
        let short = info?["CFBundleShortVersionString"] as? String ?? "—"
        let build = info?["CFBundleVersion"] as? String ?? "—"
        return "\(short) (\(build))"
    }

    private var appDisplayName: String {
        (Bundle.main.object(forInfoDictionaryKey: "CFBundleDisplayName") as? String)
            ?? (Bundle.main.object(forInfoDictionaryKey: "CFBundleName") as? String)
            ?? "__APP_NAME__"
    }

    /// 拉起系统邮箱，主题/正文预填 App 名和版本。没装邮箱时由系统自己提示。
    private func sendFeedback() {
        let subject = String(format: loc("feedback_mail_subject"), appDisplayName)
        let body = String(format: loc("feedback_mail_body"), appDisplayName, versionText)
        if let url = AppConfig.feedbackMailtoURL(subject: subject, body: body) {
            openURL(url)
        }
    }

    private func exportLogs() {
        isExporting = true
        defer { isExporting = false }
        do {
            let name = LogExport.makeFileName(prefix: "__APP_NAME__")
            let url = try LogExport.exportZip(fileName: name)
            presentMacShare(url: url)
            AppLog.logger(category: "settings").info("log export ready: \(url.lastPathComponent)")
        } catch {
            exportError = error.localizedDescription
            AppLog.logger(category: "settings").error("log export failed: \(error.localizedDescription)")
        }
    }

    /// 系统分享面板；无 key window 时退回在 Finder 中显示 zip。
    private func presentMacShare(url: URL) {
        guard let window = NSApp.keyWindow ?? NSApp.windows.first,
              let contentView = window.contentView
        else {
            NSWorkspace.shared.activateFileViewerSelecting([url])
            return
        }
        let picker = NSSharingServicePicker(items: [url])
        let rect = NSRect(
            x: contentView.bounds.midX,
            y: contentView.bounds.midY,
            width: 1,
            height: 1
        )
        picker.show(relativeTo: rect, of: contentView, preferredEdge: .minY)
    }
}
