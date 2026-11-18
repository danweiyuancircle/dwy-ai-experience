#if os(macOS)
import AppKit
import SwiftUI
import XCTest
import UniformTypeIdentifiers
@testable import DesignKitMac

@MainActor
final class MacPlatformHostTests: XCTestCase {
    func testWindowOverlayFitsAvailableSpaceWithMargins() {
        let preferred = CGSize(width: 500, height: 400)
        XCTAssertEqual(EWindowOverlayLayout.size(preferred: preferred, available: CGSize(width: 800, height: 600)),
                       preferred)
        XCTAssertEqual(EWindowOverlayLayout.size(preferred: preferred, available: CGSize(width: 360, height: 300)),
                       CGSize(width: 320, height: 260))
        XCTAssertEqual(EWindowOverlayLayout.size(preferred: preferred, available: .zero), .zero)
    }

    func testWindowOverlayMovesFocusIntoPanelAndRestoresItOnRemoval() {
        let window = NSWindow(contentRect: NSRect(x: 0, y: 0, width: 600, height: 400),
                              styleMask: [.titled], backing: .buffered, defer: false)
        window.isReleasedWhenClosed = false
        defer { window.close() }
        let original = NSTextField(frame: NSRect(x: 10, y: 10, width: 100, height: 24))
        window.contentView!.addSubview(original)
        window.makeFirstResponder(original)
        let field = NSTextField(frame: NSRect(x: 0, y: 0, width: 160, height: 24))
        let overlay = EWindowOverlayInputView(panel: field, panelSize: CGSize(width: 200, height: 100), onDismiss: {})
        overlay.frame = window.contentView!.bounds
        window.contentView!.addSubview(overlay)
        overlay.layoutSubtreeIfNeeded()
        XCTAssertTrue(overlay.ownsFirstResponder)
        XCTAssertTrue((window.firstResponder as? NSTextView)?.delegate === field || window.firstResponder === field)
        overlay.stop()
        overlay.removeFromSuperview()
        XCTAssertTrue((window.firstResponder as? NSTextView)?.delegate === original || window.firstResponder === original)
    }

    func testWindowOverlayFiltersBackgroundAndOtherWindowsAndConsumesEscape() {
        let window = NSWindow(contentRect: NSRect(x: 0, y: 0, width: 600, height: 400),
                              styleMask: [.titled], backing: .buffered, defer: false)
        window.isReleasedWhenClosed = false
        defer { window.close() }
        var dismissals = 0
        let overlay = EWindowOverlayInputView(panel: NSView(), panelSize: CGSize(width: 200, height: 100),
                                             onDismiss: { dismissals += 1 })
        overlay.frame = window.contentView!.bounds
        window.contentView!.addSubview(overlay)
        defer { overlay.stop() }
        overlay.layoutSubtreeIfNeeded()
        let background = NSEvent.mouseEvent(with: .leftMouseDown, location: CGPoint(x: 10, y: 10),
                                            modifierFlags: [], timestamp: 0, windowNumber: window.windowNumber,
                                            context: nil, eventNumber: 1, clickCount: 1, pressure: 1)!
        XCTAssertNil(overlay.filter(background))
        let inside = NSEvent.mouseEvent(with: .leftMouseDown, location: CGPoint(x: 300, y: 200),
                                        modifierFlags: [], timestamp: 0, windowNumber: window.windowNumber,
                                        context: nil, eventNumber: 2, clickCount: 1, pressure: 1)!
        XCTAssertTrue(overlay.filter(inside) === inside)
        let unrelated = NSEvent.keyEvent(with: .keyDown, location: .zero, modifierFlags: [], timestamp: 0,
                                         windowNumber: 0, context: nil, characters: "x",
                                         charactersIgnoringModifiers: "x", isARepeat: false, keyCode: 7)!
        XCTAssertTrue(overlay.filter(unrelated) === unrelated)
        let escape = NSEvent.keyEvent(with: .keyDown, location: .zero, modifierFlags: [], timestamp: 0,
                                      windowNumber: window.windowNumber, context: nil, characters: "\u{1b}",
                                      charactersIgnoringModifiers: "\u{1b}", isARepeat: false, keyCode: 53)!
        XCTAssertNil(overlay.filter(escape))
        XCTAssertEqual(dismissals, 1)
    }

    func testWindowOverlayKeepsTabInsidePanelAndLeavesCommandRoutingToAppKit() {
        let window = NSWindow(contentRect: NSRect(x: 0, y: 0, width: 600, height: 400),
                              styleMask: [.titled], backing: .buffered, defer: false)
        window.isReleasedWhenClosed = false
        defer { window.close() }
        let background = NSTextField(frame: NSRect(x: 10, y: 10, width: 100, height: 24))
        window.contentView!.addSubview(background)
        let panel = NSView(frame: NSRect(x: 0, y: 0, width: 200, height: 100))
        let first = NSTextField(frame: NSRect(x: 0, y: 50, width: 160, height: 24))
        let last = NSTextField(frame: NSRect(x: 0, y: 0, width: 160, height: 24))
        panel.addSubview(first)
        panel.addSubview(last)
        let overlay = EWindowOverlayInputView(panel: panel, panelSize: panel.frame.size, onDismiss: {})
        overlay.frame = window.contentView!.bounds
        window.contentView!.addSubview(overlay)
        defer { overlay.stop() }
        first.nextKeyView = last
        last.nextKeyView = background
        background.nextKeyView = first
        window.makeFirstResponder(last)
        let tab = NSEvent.keyEvent(with: .keyDown, location: .zero, modifierFlags: [], timestamp: 0,
                                   windowNumber: window.windowNumber, context: nil, characters: "\t",
                                   charactersIgnoringModifiers: "\t", isARepeat: false, keyCode: 48)!
        XCTAssertNil(overlay.filter(tab))
        XCTAssertTrue(overlay.ownsFirstResponder)
        XCTAssertTrue((window.firstResponder as? NSTextView)?.delegate === first || window.firstResponder === first)
        let backTab = NSEvent.keyEvent(with: .keyDown, location: .zero, modifierFlags: .shift, timestamp: 0,
                                       windowNumber: window.windowNumber, context: nil, characters: "\t",
                                       charactersIgnoringModifiers: "\t", isARepeat: false, keyCode: 48)!
        XCTAssertNil(overlay.filter(backTab))
        XCTAssertTrue((window.firstResponder as? NSTextView)?.delegate === last || window.firstResponder === last)
        let shortcut = NSEvent.keyEvent(with: .keyDown, location: .zero, modifierFlags: .command, timestamp: 0,
                                        windowNumber: window.windowNumber, context: nil, characters: "d",
                                        charactersIgnoringModifiers: "d", isARepeat: false, keyCode: 2)!
        XCTAssertTrue(overlay.filter(shortcut) === shortcut)
    }

    func testWindowOverlayRoutesTypingToPanelAndPreservesNativeEditingCommands() {
        let window = NSWindow(contentRect: NSRect(x: 0, y: 0, width: 600, height: 400),
                              styleMask: [.titled], backing: .buffered, defer: false)
        window.isReleasedWhenClosed = false
        defer { window.close() }
        let background = NSTextField(string: "unchanged")
        window.contentView!.addSubview(background)
        window.makeFirstResponder(background)
        let field = NSTextField(frame: NSRect(x: 0, y: 0, width: 160, height: 24))
        let overlay = EWindowOverlayInputView(panel: field, panelSize: CGSize(width: 200, height: 100), onDismiss: {})
        overlay.frame = window.contentView!.bounds
        window.contentView!.addSubview(overlay)
        defer { overlay.stop() }
        let typing = NSEvent.keyEvent(with: .keyDown, location: .zero, modifierFlags: [], timestamp: 0,
                                      windowNumber: window.windowNumber, context: nil, characters: "q",
                                      charactersIgnoringModifiers: "q", isARepeat: false, keyCode: 12)!
        XCTAssertNil(overlay.filter(typing))
        let editor = window.firstResponder as? NSTextView
        XCTAssertEqual(editor?.string, "q")
        XCTAssertEqual(background.stringValue, "unchanged")
        let selectAll = NSEvent.keyEvent(with: .keyDown, location: .zero, modifierFlags: .command, timestamp: 0,
                                         windowNumber: window.windowNumber, context: nil, characters: "a",
                                         charactersIgnoringModifiers: "a", isARepeat: false, keyCode: 0)!
        XCTAssertTrue(overlay.filter(selectAll) === selectAll)
        editor?.selectAll(nil)
        XCTAssertEqual(editor?.selectedRange(), NSRange(location: 0, length: 1))
    }

    func testWindowOverlayOnlyTopLayerHandlesEscapeAndRestoresLowerFocus() {
        let window = NSWindow(contentRect: NSRect(x: 0, y: 0, width: 600, height: 400),
                              styleMask: [.titled], backing: .buffered, defer: false)
        window.isReleasedWhenClosed = false
        defer { window.close() }
        var lowerDismissals = 0
        var upperDismissals = 0
        let field = NSTextField(frame: NSRect(x: 0, y: 0, width: 160, height: 24))
        let lower = EWindowOverlayInputView(panel: field, panelSize: CGSize(width: 200, height: 100),
                                           onDismiss: { lowerDismissals += 1 })
        window.contentView!.addSubview(lower)
        defer { lower.stop() }
        let upper = EWindowOverlayInputView(panel: NSView(), panelSize: CGSize(width: 200, height: 100),
                                           onDismiss: { upperDismissals += 1 })
        window.contentView!.addSubview(upper)
        let escape = NSEvent.keyEvent(with: .keyDown, location: .zero, modifierFlags: [], timestamp: 0,
                                      windowNumber: window.windowNumber, context: nil, characters: "\u{1b}",
                                      charactersIgnoringModifiers: "\u{1b}", isARepeat: false, keyCode: 53)!
        XCTAssertTrue(lower.filter(escape) === escape)
        XCTAssertNil(upper.filter(escape))
        XCTAssertEqual(lowerDismissals, 0)
        XCTAssertEqual(upperDismissals, 1)
        upper.stop()
        upper.removeFromSuperview()
        XCTAssertTrue(lower.ownsFirstResponder)
        XCTAssertNil(lower.filter(escape))
        XCTAssertEqual(lowerDismissals, 1)
    }

    func testWindowOverlayKeepsBackgroundTransparent() {
        let overlay = EWindowOverlayInputView(panel: NSView(), panelSize: CGSize(width: 100, height: 100), onDismiss: {})
        overlay.frame = NSRect(x: 0, y: 0, width: 400, height: 300)
        overlay.layoutSubtreeIfNeeded()
        let bitmap = overlay.bitmapImageRepForCachingDisplay(in: overlay.bounds)!
        overlay.cacheDisplay(in: overlay.bounds, to: bitmap)
        XCTAssertFalse(overlay.isOpaque)
        XCTAssertEqual(bitmap.colorAt(x: 10, y: 10)?.alphaComponent, 0)
    }

    func testWindowOverlayPreservesMultilineReturnAndStopsOnWindowClose() {
        let window = NSWindow(contentRect: NSRect(x: 0, y: 0, width: 600, height: 400),
                              styleMask: [.titled], backing: .buffered, defer: false)
        window.isReleasedWhenClosed = false
        let editor = NSTextView(frame: NSRect(x: 0, y: 0, width: 200, height: 100))
        var dismissals = 0
        let overlay = EWindowOverlayInputView(panel: editor, panelSize: editor.frame.size,
                                             onDismiss: { dismissals += 1 })
        window.contentView!.addSubview(overlay)
        let newline = NSEvent.keyEvent(with: .keyDown, location: .zero, modifierFlags: [], timestamp: 0,
                                       windowNumber: window.windowNumber, context: nil, characters: "\r",
                                       charactersIgnoringModifiers: "\r", isARepeat: false, keyCode: 36)!
        XCTAssertNil(overlay.filter(newline))
        XCTAssertEqual(editor.string, "\n")
        XCTAssertEqual(dismissals, 0)
        window.close()
        XCTAssertTrue(overlay.filter(newline) === newline)
    }

    func testWindowOverlayPublicModifierHostsPanelAndBlocksBackgroundShortcuts() throws {
        let window = NSWindow(contentRect: NSRect(x: 0, y: 0, width: 600, height: 400),
                              styleMask: [.titled], backing: .buffered, defer: false)
        window.isReleasedWhenClosed = false
        defer { window.close() }
        var panelActions = 0
        var backgroundActions = 0
        let hosting = NSHostingView(rootView:
            Button("Background") { backgroundActions += 1 }
                .keyboardShortcut("b")
                .frame(maxWidth: .infinity, maxHeight: .infinity)
                .eWindowOverlay(isPresented: true, preferredSize: CGSize(width: 200, height: 100), onDismiss: {}) {
                    Button("Panel") { panelActions += 1 }.keyboardShortcut("p")
                }
        )
        window.contentView = hosting
        window.makeKeyAndOrderFront(nil)
        window.makeKey()
        hosting.layoutSubtreeIfNeeded()
        RunLoop.main.run(until: Date().addingTimeInterval(0.05))
        func findOverlay(_ view: NSView) -> EWindowOverlayInputView? {
            if let overlay = view as? EWindowOverlayInputView { return overlay }
            return view.subviews.lazy.compactMap { findOverlay($0) }.first
        }
        let overlay = try XCTUnwrap(findOverlay(hosting))
        defer { overlay.stop() }
        XCTAssertEqual(overlay.panel.frame.size, CGSize(width: 200, height: 100))
        let shortcut = NSEvent.keyEvent(with: .keyDown, location: .zero, modifierFlags: .command, timestamp: 0,
                                        windowNumber: window.windowNumber, context: nil, characters: "p",
                                        charactersIgnoringModifiers: "p", isARepeat: false, keyCode: 35)!
        XCTAssertTrue(window.performKeyEquivalent(with: shortcut))
        XCTAssertEqual(panelActions, 1)
        let backgroundShortcut = NSEvent.keyEvent(with: .keyDown, location: .zero, modifierFlags: .command, timestamp: 0,
                                                  windowNumber: window.windowNumber, context: nil, characters: "b",
                                                  charactersIgnoringModifiers: "b", isARepeat: false, keyCode: 11)!
        _ = window.performKeyEquivalent(with: backgroundShortcut)
        XCTAssertEqual(backgroundActions, 0)
    }

    func testCollapseGuardOnlyChangesTheContainingSplitViewItem() {
        let controller = NSSplitViewController()
        let sidebar = NSSplitViewItem(sidebarWithViewController: NSViewController())
        let other = NSSplitViewItem(viewController: NSViewController())
        sidebar.canCollapse = true
        other.canCollapse = true
        controller.addSplitViewItem(sidebar)
        controller.addSplitViewItem(other)
        let window = NSWindow(contentViewController: controller)
        window.isReleasedWhenClosed = false
        defer { window.close() }
        window.setContentSize(NSSize(width: 800, height: 600))
        controller.view.layoutSubtreeIfNeeded()
        let attachment = SidebarCollapseAttachment()
        sidebar.viewController.view.addSubview(attachment)
        XCTAssertTrue(attachment.window === window)
        XCTAssertFalse(sidebar.canCollapse)
        XCTAssertTrue(other.canCollapse)
    }

    func testAlertKeepsResponseOrderAndMarksDestructiveAction() {
        let alert = EAlert(title: "Delete", message: "Confirm", style: .critical,
                           actions: [.init("Delete", role: .destructive), .init("Cancel", role: .cancel)])
        XCTAssertEqual(alert.nativeAlert.messageText, "Delete")
        XCTAssertEqual(alert.nativeAlert.buttons.map(\.title), ["Delete", "Cancel"])
        XCTAssertTrue(alert.nativeAlert.buttons[0].hasDestructiveAction)
        XCTAssertEqual(alert.nativeAlert.buttons[0].keyEquivalent, "")
        XCTAssertEqual(alert.nativeAlert.buttons[1].keyEquivalent, "\u{1b}")
        alert.setActionEnabled(false, at: 0)
        XCTAssertFalse(alert.nativeAlert.buttons[0].isEnabled)
    }

    func testFileDialogConfigurationPreservesDirectoryAndFileRestrictions() {
        let folder = EFileDialog.makePanel(selection: .directories, directory: URL(fileURLWithPath: "/tmp"),
                                           message: "Grant access", prompt: "Allow")
        XCTAssertTrue(folder.canChooseDirectories)
        XCTAssertFalse(folder.canChooseFiles)
        XCTAssertFalse(folder.allowsMultipleSelection)
        XCTAssertEqual(folder.prompt, "Allow")
        let files = EFileDialog.makePanel(selection: .files, allowedContentTypes: [.image])
        XCTAssertTrue(files.canChooseFiles)
        XCTAssertFalse(files.canChooseDirectories)
        XCTAssertEqual(files.allowedContentTypes, [.image])
        XCTAssertNil(EFileDialog.result(for: .cancel, panel: files))
    }

    func testAlertCancellationKeepsTheNativeSecondButtonResponse() {
        let alert = EAlert(title: "Confirmation", actions: [.init("Continue"), .init("Cancel", role: .cancel)])
        let timer = Timer(timeInterval: 0.1, target: alert.nativeAlert.buttons[1],
                          selector: #selector(NSButton.performClick(_:)), userInfo: nil, repeats: false)
        RunLoop.main.add(timer, forMode: .modalPanel)
        defer { timer.invalidate() }
        XCTAssertEqual(alert.runModal(), .alertSecondButtonReturn)
    }

    func testToolHostsKeepCloseAndLifetimePolicyAndCanHostSharedContent() {
        let panel = EToolPanel(title: "Progress", size: NSSize(width: 400, height: 180), closable: false)
        XCTAssertFalse(panel.styleMask.contains(.closable))
        XCTAssertFalse(panel.isReleasedWhenClosed)
        XCTAssertFalse(panel.hidesOnDeactivate)
        panel.setContent { EButton("Cancel", action: {}) }
        XCTAssertNotNil(panel.contentView)
        let window = EToolWindow(title: "Tool", size: NSSize(width: 640, height: 480))
        XCTAssertTrue(window.styleMask.contains(.closable))
        XCTAssertTrue(window.styleMask.contains(.resizable))
        XCTAssertFalse(window.isReleasedWhenClosed)
        window.setContent { Text("Ready") }
        XCTAssertNotNil(window.contentView)
        panel.close()
        window.close()
    }

    func testSettingsSceneAppliesWindowChromeAfterAttachment() {
        let window = NSWindow(contentRect: NSRect(x: 0, y: 0, width: 800, height: 600),
                              styleMask: [.titled, .closable], backing: .buffered, defer: false)
        window.isReleasedWhenClosed = false
        window.contentView?.addSubview(ESettingsWindowChrome.TitleView())
        XCTAssertTrue(window.styleMask.contains(.resizable))
        XCTAssertTrue(window.styleMask.contains(.miniaturizable))
        XCTAssertEqual(window.toolbarStyle, .unifiedCompact)
        window.close()
    }
}
#endif
