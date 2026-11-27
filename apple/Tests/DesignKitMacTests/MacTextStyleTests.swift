#if os(macOS)
import AppKit
import SwiftUI
import XCTest
@testable import DesignKitMac

/// 文本语义角色必须读主题字体与颜色令牌，业务页面不再裸写系统字体和 .secondary。
@MainActor
final class MacTextStyleTests: XCTestCase {
    func testRolesResolveToThemeTypographyRoles() {
        let typography = ETypography(bodySize: 15)
        XCTAssertEqual(ETextRole.body.font(typography), typography.body)
        XCTAssertEqual(ETextRole.secondary.font(typography), typography.secondary)
        XCTAssertEqual(ETextRole.caption.font(typography), typography.caption)
        XCTAssertEqual(ETextRole.title.font(typography), typography.title)
        XCTAssertEqual(ETextRole.sectionTitle.font(typography), typography.sectionTitle)
        XCTAssertEqual(ETextRole.pageTitle.font(typography), typography.pageTitle)
        XCTAssertEqual(ETextRole.monospaced.font(typography), typography.monospaced)
    }

    func testRolesResolveToThemeTextColors() {
        let colors = ESemanticColors()
        XCTAssertEqual(ETextRole.body.color(colors), colors.text)
        XCTAssertEqual(ETextRole.title.color(colors), colors.text)
        XCTAssertEqual(ETextRole.sectionTitle.color(colors), colors.text)
        XCTAssertEqual(ETextRole.pageTitle.color(colors), colors.text)
        XCTAssertEqual(ETextRole.monospaced.color(colors), colors.text)
        XCTAssertEqual(ETextRole.secondary.color(colors), colors.secondaryText)
        XCTAssertEqual(ETextRole.caption.color(colors), colors.secondaryText)
    }

    func testToneOverridesRoleColorWithSemanticColor() {
        let colors = ESemanticColors()
        XCTAssertEqual(ETextRole.caption.color(colors, tone: .failure), colors.danger)
        XCTAssertEqual(ETextRole.body.color(colors, tone: .success), colors.success)
        XCTAssertEqual(ETextRole.body.color(colors, tone: .warning), colors.warning)
        // neutral 不改变角色原有颜色，避免把正文意外降为次要色。
        XCTAssertEqual(ETextRole.body.color(colors, tone: .neutral), colors.text)
        XCTAssertEqual(ETextRole.body.color(colors, tone: nil), colors.text)
    }

    func testTextFollowsInjectedTypographyAndCoversAllInitializers() {
        let standard = measure(EText(verbatim: "Sample", role: .body), theme: EControlTheme())
        var large = EControlTheme()
        large.typography = ETypography(bodySize: 24)
        let enlarged = measure(EText(verbatim: "Sample", role: .body), theme: large)
        XCTAssertGreaterThan(enlarged.height, standard.height)

        let fromText = measure(EText(Text(verbatim: "Sample"), role: .secondary))
        let fromResource = measure(EText(LocalizedStringResource(stringLiteral: "Sample"), role: .secondary))
        XCTAssertGreaterThan(fromText.height, 0)
        XCTAssertGreaterThan(fromResource.height, 0)
    }

    func testModifierAppliesRoleToArbitraryViews() {
        var large = EControlTheme()
        large.typography = ETypography(bodySize: 24)
        let standard = measure(Label("Sample", systemImage: "star").eText(.body), theme: EControlTheme())
        let enlarged = measure(Label("Sample", systemImage: "star").eText(.body), theme: large)
        XCTAssertGreaterThan(enlarged.height, standard.height)
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
