#if os(macOS)
import AppKit
import Carbon.HIToolbox

/// Registers a physical key combination with macOS and calls the action on key release.
/// Keep the registration alive while the shortcut is enabled. The application owns its shortcut policy and persistence.
@MainActor
public final class MacGlobalHotkey {
    /// Registration can fail when macOS or another application owns the combination.
    public enum RegistrationError: Error, Equatable, Sendable {
        case invalidModifiers
        case system(OSStatus)
    }

    private static let signature: OSType = 0x4457594B // DWYK
    private static var nextID: UInt32 = 0
    private static var handler: EventHandlerRef?
    private static var registrations: [UInt32: (reference: EventHotKeyRef, invoke: () -> Void)] = [:]

    private let action: () -> Void
    let eventID: EventHotKeyID

    /// `keyCode` is the macOS virtual key code. Use at least Command, Control or Option to avoid capturing ordinary typing.
    public init(keyCode: UInt16, modifiers: NSEvent.ModifierFlags, onKeyUp: @escaping () -> Void) throws {
        let flags = try Self.carbonModifiers(for: modifiers)
        try Self.installHandlerIfNeeded()
        Self.nextID += 1
        let id = Self.nextID
        let eventID = EventHotKeyID(signature: Self.signature, id: id)
        var reference: EventHotKeyRef?
        let status = RegisterEventHotKey(UInt32(keyCode), flags, eventID,
                                         GetEventDispatcherTarget(), UInt32(kEventHotKeyExclusive), &reference)
        guard status == noErr, let reference else { throw RegistrationError.system(status) }
        self.eventID = eventID
        self.action = onKeyUp
        Self.registrations[id] = (reference, { [weak self] in self?.action() })
    }

    /// Releases the key synchronously. Call before replacing it or when disabling background shortcuts.
    public func invalidate() {
        Self.unregister(eventID.id)
    }

    deinit {
        let id = eventID.id
        // The last reference can be dropped off the main thread. The weak callback is already inactive.
        Task { @MainActor in Self.unregister(id) }
    }

    private static func unregister(_ id: UInt32) {
        guard let registration = registrations.removeValue(forKey: id) else { return }
        UnregisterEventHotKey(registration.reference)
    }

    static func carbonModifiers(for modifiers: NSEvent.ModifierFlags) throws -> UInt32 {
        let supported: NSEvent.ModifierFlags = [.command, .control, .option, .shift]
        guard supported.isSuperset(of: modifiers), !modifiers.intersection([.command, .control, .option]).isEmpty else {
            throw RegistrationError.invalidModifiers
        }
        var flags: UInt32 = 0
        if modifiers.contains(.command) { flags |= UInt32(cmdKey) }
        if modifiers.contains(.control) { flags |= UInt32(controlKey) }
        if modifiers.contains(.option) { flags |= UInt32(optionKey) }
        if modifiers.contains(.shift) { flags |= UInt32(shiftKey) }
        return flags
    }

    private static func installHandlerIfNeeded() throws {
        guard handler == nil else { return }
        let events = [
            EventTypeSpec(eventClass: OSType(kEventClassKeyboard), eventKind: UInt32(kEventHotKeyPressed)),
            EventTypeSpec(eventClass: OSType(kEventClassKeyboard), eventKind: UInt32(kEventHotKeyReleased)),
        ]
        let status = InstallEventHandler(GetEventDispatcherTarget(), { _, event, _ in
            guard let event else { return OSStatus(eventNotHandledErr) }
            var hotkey = EventHotKeyID()
            let status = GetEventParameter(event, EventParamName(kEventParamDirectObject), EventParamType(typeEventHotKeyID),
                                           nil, MemoryLayout<EventHotKeyID>.size, nil, &hotkey)
            guard status == noErr else { return OSStatus(eventNotHandledErr) }
            let released = GetEventKind(event) == UInt32(kEventHotKeyReleased)
            // The event dispatcher delivers registered hotkeys on the main event loop.
            return MainActor.assumeIsolated {
                guard hotkey.signature == MacGlobalHotkey.signature,
                      let registration = MacGlobalHotkey.registrations[hotkey.id] else {
                    return OSStatus(eventNotHandledErr)
                }
                if released { registration.invoke() }
                return noErr
            }
        }, events.count, events, nil, &handler)
        guard status == noErr else { throw RegistrationError.system(status) }
    }
}
#endif
