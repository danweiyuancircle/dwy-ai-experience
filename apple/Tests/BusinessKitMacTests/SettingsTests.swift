#if os(macOS)
import AppKit
import DesignKitMac
import SwiftUI
import XCTest
@testable import BusinessKitMac

@MainActor
final class BusinessSettingsTests: XCTestCase {
    func testTextSizePersistsAndScalesTheSuppliedTheme() throws {
        let suite = "BusinessSettingsTests.\(UUID().uuidString)"
        let defaults = try XCTUnwrap(UserDefaults(suiteName: suite))
        defer { defaults.removePersistentDomain(forName: suite) }

        var base = EControlTheme.standard
        base.colors.accent = .purple
        base.typography = ETypography(bodySize: 14)
        let preferences = BusinessPreferences(defaults: defaults)
        XCTAssertEqual(preferences.controlTheme(from: base).typography.nativeBodySize, 14)
        preferences.textSize = .large

        let restored = BusinessPreferences(defaults: defaults)
        XCTAssertEqual(restored.textSize, .large)
        XCTAssertEqual(restored.controlTheme(from: base).typography.nativeBodySize, 16)
        XCTAssertEqual(restored.controlTheme(from: base).colors.accent, .purple)
    }

    func testSettingsPanelHostsAppSectionsAndHandlesMissingSelection() {
        let general = BusinessSettingsSection(id: "general", title: Text("General"), systemImage: "gearshape") {
            ECard { Text("App-specific content") }
        }
        let tools = BusinessSettingsSection(id: "tools", title: Text("Tools"), systemImage: "wrench") {
            Text("Other options")
        }
        XCTAssertEqual(BusinessSettingsPanel.selectedSection(in: [general, tools], id: "tools")?.id, "tools")
        XCTAssertEqual(BusinessSettingsPanel.selectedSection(in: [general, tools], id: "removed")?.id, "general")
        XCTAssertNil(BusinessSettingsPanel.selectedSection(in: [], id: nil))

        _ = NSApplication.shared
        let host = NSHostingView(rootView: BusinessSettingsPanel(sections: [general, tools], onClose: {}))
        XCTAssertGreaterThanOrEqual(host.fittingSize.width, 540)
        XCTAssertGreaterThanOrEqual(host.fittingSize.height, 360)
    }

    func testBusinessSheetKeepsItsActionsOutsideScrollableContent() {
        _ = NSApplication.shared
        let view = MacBusinessSheet(title: Text("Options"), onClose: {}) {
            Text(String(repeating: "Long content. ", count: 100)).frame(width: 260)
        } footer: {
            Button("Save") {}
        }
        let host = NSHostingView(rootView: view.frame(width: 400, height: 470))
        XCTAssertEqual(host.fittingSize.width, 400, accuracy: 1)
        XCTAssertEqual(host.fittingSize.height, 470, accuracy: 1)
    }
}
#endif
