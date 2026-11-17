#if os(macOS)
import AppKit
import SwiftUI
import XCTest
import UniformTypeIdentifiers
@testable import DesignKitMac

@MainActor
final class MacPlatformHostTests: XCTestCase {
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
