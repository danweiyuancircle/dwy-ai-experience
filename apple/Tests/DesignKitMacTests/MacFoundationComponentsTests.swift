#if os(macOS)
import AppKit
import SwiftUI
import XCTest
@testable import DesignKitMac

@MainActor
final class MacFoundationComponentsTests: XCTestCase {
    func testToastChangesIdentityAndCancelsExpiryWhenAssistiveStateChanges() {
        let id = UUID()
        let normal = EToastLifetime(id: id, hovering: false, focused: false, voiceOver: false)
        let reading = EToastLifetime(id: id, hovering: false, focused: false, voiceOver: true)
        XCTAssertNotEqual(normal, reading)
        XCTAssertTrue(normal.expiresAutomatically)
        XCTAssertFalse(reading.expiresAutomatically)
        XCTAssertFalse(EToastLifetime(id: id, hovering: true, focused: false, voiceOver: false).expiresAutomatically)
        XCTAssertFalse(EToastLifetime(id: id, hovering: false, focused: true, voiceOver: false).expiresAutomatically)
        XCTAssertFalse(EToastLifetime(id: nil, hovering: false, focused: false, voiceOver: false).expiresAutomatically)
        XCTAssertNotEqual(EToastMessage("Done").id, EToastMessage("Done").id)
    }

    func testVerbatimToastDoesNotTranslateTextThatMatchesAResourceKeyAndPreservesWarningTone() throws {
        let root = FileManager.default.temporaryDirectory.appendingPathComponent(UUID().uuidString).appendingPathExtension("bundle")
        let language = root.appendingPathComponent("zh-Hans.lproj")
        try FileManager.default.createDirectory(at: language, withIntermediateDirectories: true)
        defer { try? FileManager.default.removeItem(at: root) }
        try "\"Saved\" = \"已保存\";".write(to: language.appendingPathComponent("Localizable.strings"),
                                                     atomically: true, encoding: .utf8)
        let resource = LocalizedStringResource("Saved", bundle: .atURL(root))
        let localized = EToastMessage(resource, tone: .success)
        let verbatim = EToastMessage(verbatim: "Saved", tone: .warning)
        XCTAssertEqual(localized.announcement(locale: Locale(identifier: "zh-Hans")), "已保存")
        XCTAssertEqual(verbatim.announcement(locale: Locale(identifier: "zh-Hans")), "Saved")
        XCTAssertEqual(verbatim.title, .verbatim("Saved"))
        XCTAssertEqual(verbatim.tone, .warning)
        XCTAssertEqual(verbatim.tone.symbol, "exclamationmark.triangle")
    }

    func testToastAnnouncementPreservesBundleInterpolationAndInjectedLocale() throws {
        let root = FileManager.default.temporaryDirectory.appendingPathComponent(UUID().uuidString).appendingPathExtension("bundle")
        let language = root.appendingPathComponent("zh-Hans.lproj")
        try FileManager.default.createDirectory(at: language, withIntermediateDirectories: true)
        defer { try? FileManager.default.removeItem(at: root) }
        try "\"Transferred %@\" = \"已传输 %@\";".write(to: language.appendingPathComponent("Localizable.strings"),
                                                                     atomically: true, encoding: .utf8)
        let resource = LocalizedStringResource("Transferred \("文件")", locale: Locale(identifier: "en"), bundle: .atURL(root))
        let message = EToastMessage(resource)
        XCTAssertEqual(message.announcement(locale: Locale(identifier: "zh-Hans")), "已传输 文件")
    }

    func testProgressRejectsInvalidExternalValuesInsteadOfClamping() {
        for value in [Double.nan, .infinity, -.infinity, -0.01, 1.01] {
            XCTAssertNil(EProgressFraction(value))
        }
        XCTAssertEqual(EProgressFraction(0)?.value, 0)
        XCTAssertEqual(EProgressFraction(1)?.value, 1)
        XCTAssertEqual(EProgressFraction(0.4)?.value, 0.4)
    }

    func testDefaultThemeMatchesMacGeometryAndDynamicBrandContrast() {
        let theme = EControlTheme()
        XCTAssertEqual(theme.colors.accent, EControlTheme.standard.colors.accent)
        XCTAssertEqual(theme.colors.onAccent, EControlTheme.standard.colors.onAccent)
        XCTAssertEqual(theme.iconSide, 28)
        XCTAssertEqual(theme.chromeIconSide, 34)
        XCTAssertEqual(theme.fieldHeight, 28)
        XCTAssertEqual(theme.searchHeight, 36)
        for name in [NSAppearance.Name.aqua, .darkAqua, .accessibilityHighContrastAqua, .accessibilityHighContrastDarkAqua] {
            let appearance = NSAppearance(named: name)!
            appearance.performAsCurrentDrawingAppearance {
                let accent = NSColor(theme.colors.accent).usingColorSpace(.sRGB)!
                let foreground = NSColor(theme.colors.onAccent).usingColorSpace(.sRGB)!
                let a = luminance(accent), b = luminance(foreground)
                let contrast = (max(a, b) + 0.05) / (min(a, b) + 0.05)
                XCTAssertGreaterThanOrEqual(contrast, name.rawValue.contains("HighContrast") ? 7 : 4.5)
            }
        }
    }

    func testPublicCompositionsKeepLongMessagesAndActionsMeasurable() {
        _ = NSApplication.shared
        let host = NSHostingView(rootView: VStack {
            ECard {
                ESettingsRow("A long localized setting title", detail: "Description can wrap across lines") {
                    ESwitch("Enabled", isOn: .constant(true))
                }
                ELabelValue("Value", value: Text(verbatim: "User original text"))
            }
            EStatusBadge("Failure", tone: .failure)
            ENotice("A persistent error", tone: .failure) { EButton("Retry") {} }
            EContentState(.empty, title: "Empty") { EButton("Add") {} }
            ETaskProgress("Transferring", fraction: EProgressFraction(0.4)) { EButton("Cancel") {} }
            ECheckbox("Remember", isOn: .constant(false))
        }.frame(width: 280))
        let window = NSWindow(contentRect: NSRect(x: 0, y: 0, width: 280, height: 1000),
                              styleMask: [.titled], backing: .buffered, defer: false)
        window.contentView = host
        host.layoutSubtreeIfNeeded()
        XCTAssertGreaterThan(host.fittingSize.height, 200)
        XCTAssertTrue(host.fittingSize.height.isFinite)
    }

    private func luminance(_ color: NSColor) -> Double {
        func linear(_ value: Double) -> Double { value <= 0.04045 ? value / 12.92 : pow((value + 0.055) / 1.055, 2.4) }
        return 0.2126 * linear(color.redComponent) + 0.7152 * linear(color.greenComponent) + 0.0722 * linear(color.blueComponent)
    }
}
#endif
