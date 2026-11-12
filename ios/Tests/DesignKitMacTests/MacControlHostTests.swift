#if os(macOS)
import AppKit
import SwiftUI
import XCTest
import DesignKitMac

@MainActor
final class MacControlHostTests: XCTestCase {
    func testPublicFieldShellMatchesConvenienceFieldAndSupportsNativeAccessory() {
        let direct = measure(EFieldShell { TextField("Name", text: .constant("Text")).textFieldStyle(.plain) })
        let convenience = measure(ETextField("Name", text: .constant("Text")))
        XCTAssertEqual(direct.height, convenience.height, accuracy: 0.5)
        let accessory = measure(EFieldShell {
            HStack {
                SecureField("Password", text: .constant("secret")).textFieldStyle(.plain)
                Button("Reveal") {}
            }
        })
        XCTAssertGreaterThanOrEqual(accessory.height, convenience.height)
        let search = measure(EFieldShell(isSearch: true) { TextField("Search", text: .constant("")) }
            .eControlTheme(EControlTheme(searchHeight: 52)))
        XCTAssertGreaterThanOrEqual(search.height, 52)
    }

    func testLargeTextFieldCanGrowBeyondTheNormalFieldHeight() {
        let normal = measure(ETextField("Name", text: .constant("Text")))
        let large = measure(ETextField("Name", text: .constant("Text")).font(.system(size: 40)))
        XCTAssertGreaterThanOrEqual(normal.height, 28)
        XCTAssertGreaterThan(large.height, normal.height)
    }

    func testNativeComboFontUsesTheInjectedTypographySize() throws {
        _ = NSApplication.shared
        var theme = EControlTheme()
        theme.typography.nativeBodySize = 26
        let host = NSHostingView(rootView: EComboBox("Choose", text: .constant(""), suggestions: []) { _ in }
            .eControlTheme(theme).frame(width: 320))
        let window = NSWindow(contentRect: NSRect(x: 0, y: 0, width: 320, height: 200),
                              styleMask: [.titled], backing: .buffered, defer: false)
        window.contentView = host
        host.layoutSubtreeIfNeeded()
        func find(_ view: NSView) -> NSComboBox? {
            if let combo = view as? NSComboBox { return combo }
            for child in view.subviews { if let combo = find(child) { return combo } }
            return nil
        }
        XCTAssertEqual(try XCTUnwrap(find(host)?.font).pointSize, 26)
    }

    func testThemeAppliesToSearchAndComboWithoutAdboxDependencies() {
        let theme = EControlTheme(searchHeight: 52)
        let search = measure(ESearchField("Search", text: .constant(""), clearTitle: "Clear").eControlTheme(theme))
        let combo = measure(EComboBox("Choose", text: .constant(""), suggestions: ["One"]) { _ in }
            .eControlTheme(theme))
        XCTAssertGreaterThanOrEqual(search.height, 52)
        XCTAssertGreaterThanOrEqual(combo.height, 52)
    }

    func testLongValidationMessageWrapsRatherThanClipping() {
        let short = measure(EField("Name", error: "Error") { ETextField("Name", text: .constant("")) })
        let long = measure(EField(Text("Name"), error: Text(verbatim: String(repeating: "A long validation message. ", count: 12))) {
            ETextField("Name", text: .constant(""))
        })
        XCTAssertGreaterThan(long.height, short.height)
    }

    func testPublicNativeSelectionAndMenuCompositionBuildInAHost() {
        enum Choice: Hashable { case first, second }
        let size = measure(VStack {
            EPicker("Choice", selection: .constant(Choice.first)) {
                Text("First").tag(Choice.first)
                Text("Second").tag(Choice.second)
            }
            EMenu("Actions") {
                Section("Group") {
                    Button("Action") {}
                    Toggle("Enabled", isOn: .constant(true))
                }
            }
            ESwitch("Enabled", isOn: .constant(true))
            EActionGroup {
                EButton("Save", emphasis: .primary) {}
                EIconAction("Camera", systemImage: "camera") {}
                EButton("Busy", isBusy: true) {}
            }.eControlPlacement(.floating)
            ESecureField("Password", text: .constant(""))
        })
        XCTAssertTrue(size.width.isFinite && size.height.isFinite)
        XCTAssertGreaterThan(size.height, 100)
    }

    private func measure<V: View>(_ view: V) -> NSSize {
        _ = NSApplication.shared
        let host = NSHostingView(rootView: view.frame(width: 320))
        let window = NSWindow(contentRect: NSRect(x: 0, y: 0, width: 320, height: 800),
                              styleMask: [.titled], backing: .buffered, defer: false)
        window.contentView = host
        host.layoutSubtreeIfNeeded()
        return host.fittingSize
    }
}
#endif
