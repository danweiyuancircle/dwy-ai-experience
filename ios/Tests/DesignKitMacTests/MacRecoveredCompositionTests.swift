#if os(macOS)
import AppKit
import SwiftUI
import XCTest
@testable import DesignKitMac

@MainActor
final class MacRecoveredCompositionTests: XCTestCase {
    func testSharedLayoutAliasesUseThemeRoles() {
        XCTAssertEqual(ESpace.row, EControlTheme.standard.spacing.group)
        XCTAssertEqual(ESpace.xl, EControlTheme.standard.spacing.pageInset)
        XCTAssertEqual(ERadius.control, EControlTheme.standard.fieldRadius)
    }

    func testReorderDestinationMatchesNativeInsertionSemantics() {
        XCTAssertEqual(EListMove.indices(from: IndexSet(integer: 0), to: 3, count: 3)?.target, 2)
        XCTAssertEqual(EListMove.indices(from: IndexSet(integer: 2), to: 0, count: 3)?.target, 0)
        XCTAssertNil(EListMove.indices(from: IndexSet(integer: 1), to: 2, count: 3))
        XCTAssertNil(EListMove.indices(from: IndexSet([0, 1]), to: 3, count: 3))
        XCTAssertNil(EListMove.indices(from: IndexSet(integer: 2), to: 0, count: 2))
    }

    func testSharedCompositionsHonorInjectedPageInsetAndGrowForLongContent() {
        var theme = EControlTheme()
        theme.spacing.pageInset = 40
        let compact = measure(ESettingsPage { EPageHeader(title: Text("Title")) }, theme: EControlTheme())
        let spacious = measure(ESettingsPage { EPageHeader(title: Text("Title")) }, theme: theme)
        XCTAssertGreaterThan(spacious.height, compact.height)
        let long = measure(EItemRow(isSelected: true) {
            Text(String(repeating: "A long item title ", count: 16)).fixedSize(horizontal: false, vertical: true)
        })
        let short = measure(EItemRow { Text("Short") })
        XCTAssertGreaterThan(long.height, short.height)
    }

    func testApplicationLogoUsesLocalAppAndMissingIdentityUsesSymbol() throws {
        let path = try XCTUnwrap(NSWorkspace.shared.urlForApplication(withBundleIdentifier: "com.apple.Terminal"))
        let actual = try XCTUnwrap(EApplicationIcon.image(bundleIdentifier: "com.apple.Terminal", fallbackSymbol: "terminal"))
        XCTAssertTrue(FileManager.default.fileExists(atPath: path.path))
        XCTAssertTrue(actual.isValid)
        XCTAssertFalse(actual.isTemplate)
        let fallback = try XCTUnwrap(EApplicationIcon.image(bundleIdentifier: "test.missing.application", fallbackSymbol: "terminal"))
        XCTAssertTrue(fallback.isTemplate)
        let explicitPath = try XCTUnwrap(EApplicationIcon.image(bundleIdentifier: "test.missing.application", appPath: path.path, fallbackSymbol: "terminal"))
        XCTAssertTrue(explicitPath.isValid)
        XCTAssertFalse(explicitPath.isTemplate)
    }

    func testContentStateAndFormBuildWithLocalizedAndVerbatimContent() {
        let size = measure(VStack {
            EContentState(.empty, title: Text(verbatim: "No files"), detail: Text("Choose another folder"), systemImage: "folder") { EmptyView() }
            EForm { ETextField("Name", text: .constant("")) } actions: { EButton("Save") {} }
                .frame(height: 150)
            ESidebarItem { Label("Files", systemImage: "folder") }
            List { Text("Managed item") }.modifier(EManagementListStyle()).frame(height: 60)
            EProgressPanelContent(title: Text("Processing"), fraction: EProgressFraction(0.5), hint: Text("Completed files stay available")) {
                EButton("Cancel") {}
            }
        })
        XCTAssertGreaterThan(size.height, 150)
        XCTAssertLessThanOrEqual(size.width, 321)
    }

    private func measure<V: View>(_ view: V, theme: EControlTheme = .standard) -> NSSize {
        _ = NSApplication.shared
        let host = NSHostingView(rootView: view.eControlTheme(theme).frame(width: 320))
        let window = NSWindow(contentRect: NSRect(x: 0, y: 0, width: 320, height: 800), styleMask: [.titled], backing: .buffered, defer: false)
        window.contentView = host
        host.layoutSubtreeIfNeeded()
        return host.fittingSize
    }
}
#endif
