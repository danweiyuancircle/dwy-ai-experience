#if os(macOS)
import Foundation
import SyncCore
import Testing
@testable import BusinessKitMac

@MainActor
struct WorkflowTests {
    @Test
    func shortcutPersistenceKeepsExplicitlyDisabledDefaultsAndSupportsReset() throws {
        try withDefaults { defaults in
            let first = try #require(BusinessShortcut(key: "K", modifiers: [.command, .shift]))
            let second = try #require(BusinessShortcut(key: "u", modifiers: [.command, .shift]))
            let actions = [
                BusinessShortcutAction(id: "open", title: "Open", defaultShortcut: first),
                BusinessShortcutAction(id: "run", title: "Run"),
            ]
            let store = try BusinessShortcutStore(actions: actions, defaults: defaults, storageKey: "bindings")
            try store.assign(nil, to: "open")
            try store.assign(second, to: "run")

            let reopened = try BusinessShortcutStore(actions: actions, defaults: defaults, storageKey: "bindings")
            #expect(reopened.shortcut(for: "open") == nil)
            #expect(reopened.shortcut(for: "run") == second)
            #expect(first.key == "k")
            try reopened.reset("open")
            #expect(reopened.shortcut(for: "open") == first)
            try reopened.resetAll()
            #expect(reopened.shortcut(for: "run") == nil)
        }
    }

    @Test
    func reservedAndDuplicateShortcutsLeavePriorMappingsIntact() throws {
        try withDefaults { defaults in
            let first = try #require(BusinessShortcut(key: "s", modifiers: [.command, .shift]))
            let quit = try #require(BusinessShortcut(key: "q", modifiers: .command))
            let additionalReserved = try #require(BusinessShortcut(key: "p", modifiers: .command))
            let store = try BusinessShortcutStore(
                actions: [.init(id: "open", title: "Open", defaultShortcut: first), .init(id: "run", title: "Run")],
                defaults: defaults,
                storageKey: "bindings",
                reserved: [additionalReserved]
            )
            #expect(throws: BusinessShortcutError.conflict("Open")) { try store.assign(first, to: "run") }
            #expect(throws: BusinessShortcutError.reservedShortcut) { try store.assign(quit, to: "run") }
            #expect(throws: BusinessShortcutError.reservedShortcut) { try store.assign(additionalReserved, to: "run") }
            #expect(store.shortcut(for: "open") == first)
            #expect(store.shortcut(for: "run") == nil)
            #expect(defaults.data(forKey: "bindings") == nil)
            #expect(BusinessShortcut(key: "a", modifiers: .shift) == nil)
        }
    }

    @Test
    func failedGlobalRegistrationRetainsPreviouslySavedShortcut() throws {
        enum RegistrationError: Error { case conflict }
        try withDefaults { defaults in
            let first = try #require(BusinessShortcut(key: "k", modifiers: [.control, .option]))
            let conflict = try #require(BusinessShortcut(key: "u", modifiers: [.control, .option]))
            let actions = [BusinessShortcutAction(id: "toggle", title: "Toggle", scope: .global)]
            var registered: [String: BusinessShortcut] = [:]
            let store = try BusinessShortcutStore(actions: actions, defaults: defaults, storageKey: "global") { mapping in
                if mapping["toggle"] == conflict { throw RegistrationError.conflict }
                registered = mapping
            }
            try store.activateGlobalShortcuts()
            try store.assign(first, to: "toggle")
            #expect(throws: RegistrationError.conflict) { try store.assign(conflict, to: "toggle") }
            #expect(registered["toggle"] == first)
            #expect(store.shortcut(for: "toggle") == first)

            let reopened = try BusinessShortcutStore(actions: actions, defaults: defaults, storageKey: "global")
            #expect(reopened.shortcut(for: "toggle") == first)
            #expect(throws: BusinessShortcutError.globalRegistrationUnavailable) { try reopened.assign(nil, to: "toggle") }
        }
    }

    @Test
    func corruptShortcutsArePreservedUntilExplicitReset() throws {
        try withDefaults { defaults in
            let corrupt = Data([0xff])
            defaults.set(corrupt, forKey: "bindings")
            let store = try BusinessShortcutStore(
                actions: [.init(id: "open", title: "Open")], defaults: defaults, storageKey: "bindings"
            )
            #expect(store.loadError == .unreadableSettings)
            #expect(throws: BusinessShortcutError.unreadableSettings) { try store.assign(nil, to: "open") }
            #expect(defaults.data(forKey: "bindings") == corrupt)
            try store.resetAll()
            #expect(store.loadError == nil)
        }
    }

    @Test
    func reviewThresholdAndCooldownSurviveRecreation() throws {
        try withDefaults { defaults in
            let now = Date(timeIntervalSince1970: 10_000)
            let first = BusinessReviewPrompter(storageKey: "review", defaults: defaults, minimumSuccessfulEvents: 2, cooldown: 100)
            #expect(!first.recordSuccessfulEvent(now: now))
            #expect(first.recordSuccessfulEvent(now: now))

            let reopened = BusinessReviewPrompter(storageKey: "review", defaults: defaults, minimumSuccessfulEvents: 2, cooldown: 100)
            #expect(!reopened.recordSuccessfulEvent(now: now.addingTimeInterval(10)))
            #expect(!reopened.recordSuccessfulEvent(now: now.addingTimeInterval(99)))
            #expect(reopened.recordSuccessfulEvent(now: now.addingTimeInterval(100)))
            #expect(!reopened.recordSuccessfulEvent(now: now.addingTimeInterval(200)))
        }
    }

    @Test
    func syncActionExcludesUnavailableAndAlreadyRunningPhases() {
        let available: [SyncPhase] = [.idle, .failed, .waitingForRetry]
        let unavailable: [SyncPhase] = [.localOnly, .syncing, .paused, .requiresAuthentication, .identityChanged]
        #expect(available.allSatisfy { BusinessSyncView.presentation(for: $0).canSynchronize })
        #expect(unavailable.allSatisfy { !BusinessSyncView.presentation(for: $0).canSynchronize })
    }

    private func withDefaults(_ action: (UserDefaults) throws -> Void) throws {
        let suite = "BusinessKitMac.WorkflowTests.\(UUID().uuidString)"
        let defaults = try #require(UserDefaults(suiteName: suite))
        defer { defaults.removePersistentDomain(forName: suite) }
        try action(defaults)
    }
}
#endif
