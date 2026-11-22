import AppKit
import AuthCore
import BusinessKitMac
import DesignKitMac
import LogKit
import SwiftUI
import SyncCore

@main
struct MacBusinessGallery: App {
    @State private var preferences = BusinessPreferences()
    @State private var shortcuts = Result { try makeGalleryShortcuts() }
    @State private var account = makeGalleryAccount()

    init() {
        let logs = FileManager.default.temporaryDirectory.appendingPathComponent("MacBusinessGallery-Logs", isDirectory: true)
        AppLog.bootstrap(config: LogConfig(subsystem: "com.dwy.mac-business-gallery", directoryURL: logs, alsoLogToConsole: false))
        AppLog.info("Mac business component gallery opened.")
    }

    var body: some Scene {
        Window("Mac Business Kit", id: "business") {
            BusinessGalleryHome(preferences: preferences, shortcuts: shortcuts, account: account)
                .businessPreferences(preferences)
                .onAppear {
                    NSApp.setActivationPolicy(.regular)
                    NSApp.activate()
                }
        }
        .defaultSize(width: 800, height: 600)

        Settings {
            gallerySettings(preferences: preferences, shortcuts: shortcuts, account: account)
                .businessPreferences(preferences)
                .background { ESettingsWindowChrome().frame(width: 0, height: 0) }
        }
    }
}

private struct BusinessGalleryHome: View {
    let preferences: BusinessPreferences
    let shortcuts: Result<BusinessShortcutStore, any Error>
    let account: AuthSessionStore
    @State private var showSettings = false
    @State private var showHelp = false
    @State private var showForm = false
    @State private var showPaywall = false
    @State private var purchasedProducts: Set<String> = []
    @State private var purchaseMessage: Text?
    @State private var note = ""
    @State private var review = BusinessReviewPrompter(storageKey: "demo.review", minimumSuccessfulEvents: 3, cooldown: 60)
    @State private var reviewMessage: Text?

    var body: some View {
        ESettingsPage(maxContentWidth: 640) {
            EPageHeader(
                title: Text("Mac Business Kit"),
                subtitle: Text("Shared settings and business flows")
            )
            ECard {
                ESettingsRow(Text("Settings")) {
                    EButton("Open Sheet") { showSettings = true }
                }
                Divider()
                ESettingsRow(Text("Demo Purchase"), detail: purchaseMessage) {
                    EButton("Open Paywall") { showPaywall = true }
                }
                Divider()
                ESettingsRow(Text("Help and Feedback")) {
                    EButton("Open Help") { showHelp = true }
                }
                Divider()
                ESettingsRow(Text("File Actions")) {
                    MacFileActions(fileName: "example.txt") { .data(Data("Example export\n".utf8)) }
                }
                Divider()
                ESettingsRow(Text("Diagnostics")) {
                    MacFileActions.logs(fileNamePrefix: "MacBusinessGallery")
                }
                Divider()
                ESettingsRow(Text("Form Sheet and Shortcut")) {
                    EButton("Open Form") { showForm = true }
                        .keyboardShortcut((try? shortcuts.get())?.shortcut(for: "show-form")?.keyboardShortcut)
                }
                Divider()
                ESettingsRow(Text("Review Eligibility"), detail: reviewMessage) {
                    EButton("Record Action") {
                        reviewMessage = review.recordSuccessfulEvent()
                            ? Text("Eligible to request a rating") : Text("Action recorded")
                    }
                }
            }
        }
        .sheet(isPresented: $showSettings) {
            gallerySettings(preferences: preferences, shortcuts: shortcuts, account: account,
                            onClose: { showSettings = false })
        }
        .sheet(isPresented: $showHelp) {
            MacHelpCenter(
                title: Text("Gallery Help"),
                topics: [
                    MacHelpTopic(id: "privacy", title: Text("What does this example store?"),
                                 summary: Text("Appearance and shortcut settings are saved locally. Account and purchases are simulated.")),
                ],
                contacts: [
                    MacFeedbackContact(id: "reference", title: Text("Copy Example Reference"), action: .copy("gallery-example")),
                ],
                onClose: { showHelp = false }
            )
            .frame(minWidth: 480, minHeight: 420)
        }
        .sheet(isPresented: $showForm) {
            MacBusinessSheet(title: Text("Example Form"), onClose: { showForm = false }) {
                ECard {
                    ESettingsRow(Text("Note")) { ETextField(Text("Note"), text: $note) }
                }
            } footer: {
                HStack {
                    Spacer()
                    EButton("Done", emphasis: .primary) { showForm = false }
                        .keyboardShortcut(.defaultAction)
                }
            }
            .frame(width: 460, height: 320)
        }
        .macPaywall(
            isPresented: $showPaywall,
            configuration: MacPaywallConfiguration(
                title: "Unlock the Preview",
                subtitle: "This is a local simulation. No payment will be made.",
                plans: [
                    MacPaywallPlan(id: "annual", title: "Annual", detail: "Simulated subscription", isRecommended: true),
                    MacPaywallPlan(id: "lifetime", title: "Lifetime", detail: "Simulated one-time purchase"),
                ],
                features: [MacPaywallFeature(title: "Export files", free: "Limited", paid: "Included")]
            ),
            store: MacPaywallStore(
                snapshot: { MacPaywallSnapshot(prices: ["annual": "$9.99", "lifetime": "$14.99"],
                                              purchasedProductIDs: purchasedProducts) },
                load: {},
                purchase: { product in
                    purchasedProducts.insert(product)
                    return .purchased
                },
                restore: {}
            ),
            onUnlocked: { _ in purchaseMessage = Text("Simulated purchase completed") }
        )
    }
}

@MainActor
private func gallerySettings(
    preferences: BusinessPreferences,
    shortcuts: Result<BusinessShortcutStore, any Error>,
    account: AuthSessionStore,
    onClose: (() -> Void)? = nil
) -> some View {
    BusinessSettingsPanel(sections: [
        BusinessSettingsSection(id: "general", title: Text("General"), systemImage: "slider.horizontal.3") {
            BusinessGeneralSettings(preferences: preferences)
        },
        BusinessSettingsSection(id: "shortcuts", title: Text("Shortcuts"), systemImage: "command") {
            switch shortcuts {
            case .success(let store): BusinessShortcutsView(store: store)
            case .failure: EContentState(.failure, title: Text("Shortcuts could not be initialized")) { EmptyView() }
            }
        },
        BusinessSettingsSection(id: "account", title: Text("Account and Sync"), systemImage: "person.crop.circle") {
            BusinessAccountView(session: account, signIn: { try await account.signIn() })
            BusinessSyncView(state: SyncState(phase: .localOnly, pendingCount: 0, conflictCount: 0,
                                              lastSuccessfulSync: nil, errorCode: nil))
        },
        BusinessSettingsSection(id: "about", title: Text("About"), systemImage: "info.circle") {
            BusinessAboutSettings()
        },
    ], onClose: onClose)
}

@MainActor
private func makeGalleryShortcuts() throws -> BusinessShortcutStore {
    try BusinessShortcutStore(actions: [
        BusinessShortcutAction(
            id: "show-form", title: "Open Example Form",
            defaultShortcut: BusinessShortcut(key: "k", modifiers: [.command, .shift])
        ),
    ], storageKey: "demo.shortcuts")
}
