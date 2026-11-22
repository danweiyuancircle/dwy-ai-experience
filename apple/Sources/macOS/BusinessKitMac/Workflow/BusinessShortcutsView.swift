#if os(macOS)
import DesignKitMac
import SwiftUI

func workflowText(_ key: LocalizedStringKey) -> Text {
    Text(key, tableName: "Workflow", bundle: .module)
}

/// 录入、停用和恢复宿主提供的命令。可直接作为设置页的内容。
public struct BusinessShortcutsView: View {
    private let store: BusinessShortcutStore
    @Environment(\.eControlTheme) private var theme
    @FocusState private var focusedAction: String?
    @State private var recording: String?
    @State private var error: LocalizedStringKey?
    @State private var confirmingReset = false

    public init(store: BusinessShortcutStore) { self.store = store }

    public var body: some View {
        VStack(alignment: .leading, spacing: theme.spacing.group) {
            EPageHeader(title: workflowText("shortcuts.title"))
            if store.actions.isEmpty {
                EContentState(.empty, title: workflowText("shortcuts.empty"), systemImage: "keyboard") { EmptyView() }
            } else {
                ECard {
                    VStack(alignment: .leading, spacing: theme.spacing.controlGroup) {
                        ForEach(store.actions) { action in
                            row(for: action)
                        }
                    }
                }
                if let issue = error ?? store.loadError.map(message(for:)) {
                    EStatusBadge(workflowText(issue), tone: .failure)
                        .accessibilityAddTraits(.updatesFrequently)
                }
                EButton(emphasis: .secondary, action: { confirmingReset = true }) {
                    workflowText("shortcuts.resetAll")
                }
            }
        }
        .onChange(of: focusedAction) { _, next in
            if recording != next { recording = nil }
        }
        .confirmationDialog(workflowText("shortcuts.resetTitle"), isPresented: $confirmingReset) {
            Button(role: .destructive) { update { try store.resetAll() } } label: {
                workflowText("shortcuts.resetAll")
            }
            Button(role: .cancel) {} label: { workflowText("common.cancel") }
        }
    }

    private func row(for action: BusinessShortcutAction) -> some View {
        let global = action.scope == .global
        let available = !global || store.canRegisterGlobalShortcuts
        return ESettingsRow(
            Text(verbatim: action.title),
            detail: workflowText(global ? (available ? "shortcuts.global" : "shortcuts.globalUnavailable") : "shortcuts.application")
        ) {
            HStack(spacing: theme.spacing.inline) {
                EButton(emphasis: .secondary, action: {
                    recording = action.id
                    focusedAction = action.id
                    error = nil
                }) {
                    if recording == action.id {
                        workflowText("shortcuts.recording")
                    } else if let shortcut = store.shortcut(for: action.id) {
                        Text(verbatim: shortcut.keyCap).monospaced()
                    } else {
                        workflowText("shortcuts.record")
                    }
                }
                .focusable()
                .focused($focusedAction, equals: action.id)
                .onKeyPress(phases: .down) { press in
                    capture(press, for: action.id)
                }
                .accessibilityHint(workflowText("shortcuts.recordHint"))
                if store.shortcut(for: action.id) != nil {
                    EButton(emphasis: .secondary, action: { update { try store.assign(nil, to: action.id) } }) {
                        workflowText("shortcuts.clear")
                    }
                }
                EButton(emphasis: .secondary, action: { update { try store.reset(action.id) } }) {
                    workflowText("shortcuts.reset")
                }
            }
            .disabled(!available || store.loadError != nil)
        }
    }

    private func capture(_ press: KeyPress, for id: String) -> KeyPress.Result {
        guard recording == id else { return .ignored }
        if press.modifiers.isEmpty {
            if press.key == .escape {
                recording = nil
                return .handled
            }
            if press.key == .tab { return .ignored }
        }
        var modifiers: BusinessShortcut.Modifiers = []
        if press.modifiers.contains(.command) { modifiers.insert(.command) }
        if press.modifiers.contains(.option) { modifiers.insert(.option) }
        if press.modifiers.contains(.control) { modifiers.insert(.control) }
        if press.modifiers.contains(.shift) { modifiers.insert(.shift) }
        guard let shortcut = BusinessShortcut(key: press.key.character, modifiers: modifiers) else {
            error = "shortcuts.invalidModifiers"
            return .handled
        }
        update { try store.assign(shortcut, to: id) }
        if error == nil { recording = nil }
        return .handled
    }

    private func update(_ operation: () throws -> Void) {
        do {
            try operation()
            error = nil
        } catch let failure as BusinessShortcutError {
            error = message(for: failure)
        } catch {
            self.error = "shortcuts.registrationFailed"
        }
    }

    private func message(for error: BusinessShortcutError) -> LocalizedStringKey {
        switch error {
        case .invalidConfiguration, .unknownAction: "shortcuts.configurationFailed"
        case .unreadableSettings: "shortcuts.unreadable"
        case .reservedShortcut: "shortcuts.reserved"
        case .conflict(let title): "shortcuts.conflict \(title)"
        case .globalRegistrationUnavailable: "shortcuts.globalUnavailable"
        }
    }
}
#endif
