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
        XCTAssertEqual(theme.fieldRadius, 8)
        XCTAssertEqual(theme.cardRadius, 8)
        XCTAssertEqual(theme.typography.nativeBodySize, 13)
        XCTAssertEqual(theme.typography.body, .system(size: 13))
        XCTAssertEqual(theme.typography.secondary, .system(size: 11))
        for name in [NSAppearance.Name.aqua, .darkAqua, .accessibilityHighContrastAqua, .accessibilityHighContrastDarkAqua] {
            let colors = ESemanticColors(appearance: name)
            let increasedContrast = name == .accessibilityHighContrastAqua || name == .accessibilityHighContrastDarkAqua
            let isDark = name == .darkAqua || name == .accessibilityHighContrastDarkAqua
            XCTAssertEqual(rgb(colors.background), isDark ? 0x0A0A0B : 0xFAFAFA)
            XCTAssertEqual(rgb(colors.surface), isDark ? 0x18181B : 0xFFFFFF)
            XCTAssertEqual(rgb(colors.elevatedSurface), isDark ? 0x1F1F23 : 0xFFFFFF)
            XCTAssertEqual(rgb(colors.accent), increasedContrast
                           ? (isDark ? 0x93C5FD : 0x1E40AF)
                           : (isDark ? 0x3B82F6 : 0x2563EB))
            let minimum = increasedContrast ? 7.0 : 4.5
            XCTAssertGreaterThanOrEqual(contrast(colors.accent, colors.onAccent), minimum)
            for foreground in [colors.text, colors.secondaryText, colors.tertiaryText, colors.success, colors.warning, colors.danger] {
                for background in [colors.background, colors.surface, colors.elevatedSurface, colors.canvas] {
                    XCTAssertGreaterThanOrEqual(contrast(foreground, background), minimum, "\(name.rawValue)")
                }
            }
            if increasedContrast {
                XCTAssertGreaterThanOrEqual(contrast(colors.separator, colors.surface), 3)
            }
        }
    }

    func testSharedColorsResolveUsingAppKitEffectiveAppearance() {
        let dynamic = EControlTheme.standard.colors
        let roles: [KeyPath<ESemanticColors, Color>] = [\.background, \.surface, \.elevatedSurface, \.secondaryText, \.separator, \.accent, \.danger]
        for name in [NSAppearance.Name.aqua, .darkAqua] {
            NSAppearance(named: name)!.performAsCurrentDrawingAppearance {
                let resolved = ESemanticColors(appearance: NSAppearance.currentDrawing().name)
                for role in roles {
                    XCTAssertEqual(rgb(dynamic[keyPath: role]), rgb(resolved[keyPath: role]))
                }
            }
        }
    }

    func testCustomAccentDrivesHoverUnlessAppOverridesIt() {
        var theme = EControlTheme.standard
        theme.accent = .purple
        XCTAssertEqual(theme.colors.hover, Color.purple.opacity(0.07))
        theme.colors.hover = .mint
        theme.accent = .orange
        XCTAssertEqual(theme.colors.hover, .mint)
        XCTAssertEqual(EnvironmentValues().eControlTheme.colors.accent, EControlTheme.standard.colors.accent)
    }

    func testSharedCardRendersLightDarkAndInjectedSurface() throws {
        _ = NSApplication.shared
        let standard = EControlTheme.standard
        var custom = standard
        custom.colors.surface = Color(red: 0, green: 0, blue: 1)
        let samples: [(ColorScheme, EControlTheme, Color)] = [
            (.light, standard, ESemanticColors(appearance: .aqua).surface),
            (.dark, standard, ESemanticColors(appearance: .darkAqua).surface),
            (.dark, custom, custom.colors.surface),
        ]
        for (scheme, theme, expected) in samples {
            // 用同一张图的参考色消除显示色域和渲染色域的换算差异。
            let renderer = ImageRenderer(content: HStack(spacing: 0) {
                ECard { Color.clear.frame(height: 36) }.frame(width: 120)
                expected.frame(width: 120, height: 60)
            }.eControlTheme(theme).environment(\.colorScheme, scheme))
            let image = try XCTUnwrap(renderer.cgImage)
            let bitmap = NSBitmapImageRep(cgImage: image)
            let card = try XCTUnwrap(bitmap.colorAt(x: image.width / 4, y: image.height / 2))
            let swatch = try XCTUnwrap(bitmap.colorAt(x: image.width * 3 / 4, y: image.height / 2))
            XCTAssertEqual(card, swatch)
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

    private func rgb(_ color: Color) -> UInt32 {
        let resolved = NSColor(color).usingColorSpace(.sRGB)!
        return [resolved.redComponent, resolved.greenComponent, resolved.blueComponent].reduce(0) {
            ($0 << 8) | UInt32(($1 * 255).rounded())
        }
    }

    private func contrast(_ foreground: Color, _ background: Color) -> Double {
        let a = luminance(foreground), b = luminance(background)
        return (max(a, b) + 0.05) / (min(a, b) + 0.05)
    }

    private func luminance(_ swiftUIColor: Color) -> Double {
        let color = NSColor(swiftUIColor).usingColorSpace(.sRGB)!
        func linear(_ value: Double) -> Double { value <= 0.04045 ? value / 12.92 : pow((value + 0.055) / 1.055, 2.4) }
        return 0.2126 * linear(color.redComponent) + 0.7152 * linear(color.greenComponent) + 0.0722 * linear(color.blueComponent)
    }
}
#endif
