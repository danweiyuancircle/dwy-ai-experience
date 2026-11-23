#if os(macOS)
import AppKit
import Carbon.HIToolbox
import Testing
@testable import BusinessKitMac

@MainActor
struct MacGlobalHotkeyTests {
    @Test
    func rejectsUnmodifiedAndUnsupportedCombinations() throws {
        #expect(throws: MacGlobalHotkey.RegistrationError.invalidModifiers) {
            try MacGlobalHotkey(keyCode: UInt16(kVK_ANSI_K), modifiers: .shift) {}
        }
        #expect(throws: MacGlobalHotkey.RegistrationError.invalidModifiers) {
            try MacGlobalHotkey(keyCode: UInt16(kVK_ANSI_K), modifiers: [.command, .capsLock]) {}
        }
        let flags = try MacGlobalHotkey.carbonModifiers(for: [.command, .control, .option, .shift])
        #expect(flags == UInt32(cmdKey | controlKey | optionKey | shiftKey))
    }

    @Test
    func competingRegistrationFailsAndInvalidationReleasesTheCombination() throws {
        let keyCode = UInt16(kVK_F18)
        let modifiers: NSEvent.ModifierFlags = [.command, .control, .option, .shift]
        let registration = try MacGlobalHotkey(keyCode: keyCode, modifiers: modifiers) {}
        defer { registration.invalidate() }

        #expect(throws: MacGlobalHotkey.RegistrationError.self) {
            try MacGlobalHotkey(keyCode: keyCode, modifiers: modifiers) {}
        }
        registration.invalidate()
        let replacement = try MacGlobalHotkey(keyCode: keyCode, modifiers: modifiers) {}
        registration.invalidate()
        defer { replacement.invalidate() }
        #expect(throws: MacGlobalHotkey.RegistrationError.self) {
            try MacGlobalHotkey(keyCode: keyCode, modifiers: modifiers) {}
        }
    }

    @Test
    func dispatchesOnlyThisRegistrationOnRelease() throws {
        var releases = 0
        let registration = try MacGlobalHotkey(keyCode: UInt16(kVK_F19), modifiers: [.command, .control, .option]) {
            releases += 1
        }
        defer { registration.invalidate() }

        #expect(try send(kEventHotKeyPressed, id: registration.eventID) == noErr)
        #expect(releases == 0)
        #expect(try send(kEventHotKeyReleased, id: .init(signature: 0, id: registration.eventID.id)) == eventNotHandledErr)
        #expect(try send(kEventHotKeyReleased, id: registration.eventID) == noErr)
        #expect(releases == 1)
        registration.invalidate()
        #expect(try send(kEventHotKeyReleased, id: registration.eventID) == eventNotHandledErr)
        #expect(releases == 1)
    }

    private func send(_ kind: Int, id: EventHotKeyID) throws -> OSStatus {
        var eventRef: EventRef?
        let status = CreateEvent(nil, OSType(kEventClassKeyboard), UInt32(kind), 0, 0, &eventRef)
        try #require(status == noErr)
        let event = try #require(eventRef)
        defer { ReleaseEvent(event) }
        var id = id
        let parameterStatus = SetEventParameter(event, EventParamName(kEventParamDirectObject), EventParamType(typeEventHotKeyID),
                                                MemoryLayout<EventHotKeyID>.size, &id)
        try #require(parameterStatus == noErr)
        return SendEventToEventTarget(event, GetEventDispatcherTarget())
    }
}
#endif
