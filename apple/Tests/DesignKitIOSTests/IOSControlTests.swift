#if os(iOS)
import XCTest
import SwiftUI
import UIKit
@testable import DesignKitIOS

@MainActor
final class IOSControlTests: XCTestCase {
    func testProgressRejectsNonFiniteAndOutOfRangeValues() {
        for value in [Double.nan, .infinity, -.infinity, -0.01, 1.01] {
            XCTAssertThrowsError(try EProgressValue(fraction: value)) { error in
                XCTAssertEqual(error as? EProgressValue.ValidationError, .invalidFraction)
            }
        }
    }

    func testProgressPreservesValidBoundaryValues() throws {
        for value in [0.0, 0.25, 1.0] {
            XCTAssertEqual(try EProgressValue(fraction: value).fraction, value)
        }
    }

    func testStandardGeometryUsesPhysicalPixelAndAdaptiveInsets() {
        let theme = EControlTheme.standard
        XCTAssertEqual(theme.hairline(displayScale: 3), 1 / 3, accuracy: 0.0001)
        XCTAssertEqual(theme.spacing.pageInset(horizontalSizeClass: .compact), 16)
        XCTAssertEqual(theme.spacing.pageInset(horizontalSizeClass: .regular), 24)
        XCTAssertEqual(theme.size.iconHit, 44)
        XCTAssertEqual(theme.size.field, 44)
    }

    func testBrandOverrideCannotChangeDangerAndBodyRoles() {
        let standard = EControlTheme.standard
        let custom = EControlTheme(accent: EAccentColors(
            light: .purple, onLight: .white, dark: .cyan, onDark: .black,
            highContrastLight: .black, onHighContrastLight: .white,
            highContrastDark: .white, onHighContrastDark: .black
        ))
        XCTAssertEqual(standard.colors.danger, custom.colors.danger)
        XCTAssertEqual(standard.colors.primary, custom.colors.primary)
        XCTAssertEqual(custom.accentPair(scheme: .dark, contrast: .increased).accent, .white)
        XCTAssertEqual(custom.accentPair(scheme: .light, contrast: .standard).accent, .purple)
    }

    func testRepeatedMessagesHaveDistinctIdentityAndVerbatimIsPreserved() {
        let first = ENotice(verbatim: "  user.key \n")
        let second = ENotice(verbatim: "  user.key \n")
        XCTAssertNotEqual(first.id, second.id)
        XCTAssertEqual(first.announcement(locale: Locale(identifier: "en")), "  user.key \n")
        XCTAssertFalse(first.isTransient)
    }

    func testAnnouncementUsesHostLocaleAndOriginalResourceBundle() throws {
        let url = FileManager.default.temporaryDirectory.appendingPathComponent(UUID().uuidString + ".bundle")
        defer { try? FileManager.default.removeItem(at: url) }
        for (language, format) in [("en", "%lld items"), ("zh-Hans", "%lld 个项目")] {
            let directory = url.appendingPathComponent(language + ".lproj")
            try FileManager.default.createDirectory(at: directory, withIntermediateDirectories: true)
            try "\"item_count %lld\" = \"\(format)\";".write(
                to: directory.appendingPathComponent("Localizable.strings"), atomically: true, encoding: .utf8
            )
        }
        let count = 3
        let resource = LocalizedStringResource("item_count \(count)", bundle: .atURL(url))
        let notice = ENotice(resource)
        XCTAssertEqual(notice.announcement(locale: Locale(identifier: "en")), "3 items")
        XCTAssertEqual(notice.announcement(locale: Locale(identifier: "zh-Hans")), "3 个项目")
    }

    func testPersistentReplacementSurvivesOldTimer() async throws {
        let center = ENoticeCenter(dismissAfter: .milliseconds(10))
        center.show(.transientSuccess("Saved"))
        let replacement = ENotice(verbatim: "Read this failure", tone: .error)
        center.show(replacement)
        try await Task.sleep(for: .milliseconds(40))
        XCTAssertEqual(center.notice?.id, replacement.id)
    }

    func testTransientSuccessDismissesAndExplicitCancellationRetainsMessage() async throws {
        let center = ENoticeCenter(dismissAfter: .milliseconds(10))
        center.show(.transientSuccess("Saved"))
        try await Task.sleep(for: .milliseconds(40))
        XCTAssertNil(center.notice)
        let retained = ENotice.transientSuccess("Saved again")
        center.show(retained)
        center.cancelPendingDismissal()
        try await Task.sleep(for: .milliseconds(40))
        XCTAssertEqual(center.notice?.id, retained.id)
        center.dismiss()
        XCTAssertNil(center.notice)
    }

    func testVoiceOverKeepsTransientMessageUntilDismissed() async throws {
        let center = ENoticeCenter(dismissAfter: .milliseconds(10))
        center.updateAccessibility(voiceOverEnabled: true)
        let notice = ENotice.transientSuccess("Saved")
        center.show(notice)
        try await Task.sleep(for: .milliseconds(40))
        XCTAssertEqual(center.notice?.id, notice.id)
        center.updateAccessibility(voiceOverEnabled: false)
        try await Task.sleep(for: .milliseconds(40))
        XCTAssertNil(center.notice)
    }

    func testInteractionPausesTimerAndReplacementRemainsPaused() async throws {
        let center = ENoticeCenter(dismissAfter: .milliseconds(10))
        center.show(.transientSuccess("Saved"))
        center.updateInteraction(active: true)
        let replacement = ENotice.transientSuccess("Saved again")
        center.show(replacement)
        try await Task.sleep(for: .milliseconds(40))
        XCTAssertEqual(center.notice?.id, replacement.id)
        center.updateInteraction(active: false)
        try await Task.sleep(for: .milliseconds(40))
        XCTAssertNil(center.notice)
    }

    func testTransientVerbatimPreservesToneSymbolAndRestartsForIdenticalText() async throws {
        let center = ENoticeCenter(dismissAfter: .milliseconds(80))
        let first = ENotice.transient(verbatim: "  copied.key  ", tone: .neutral, systemImage: "arrow.down.to.line")
        XCTAssertEqual(first.announcement(locale: Locale(identifier: "zh-Hans")), "  copied.key  ")
        XCTAssertEqual(first.tone, .neutral)
        XCTAssertEqual(first.systemImage, "arrow.down.to.line")
        center.show(first)
        try await Task.sleep(for: .milliseconds(50))
        let second = ENotice.transient(verbatim: "  copied.key  ")
        center.show(second)
        XCTAssertNotEqual(first.id, second.id)
        try await Task.sleep(for: .milliseconds(50))
        XCTAssertEqual(center.notice?.id, second.id)
        try await Task.sleep(for: .milliseconds(80))
        XCTAssertNil(center.notice)
    }

    func testFeedbackIsCompactAndGrowsWithoutClippingForAccessibility() {
        let toast = EToast(Text(verbatim: "已复制"))
        let toastSize = UIHostingController(rootView: toast).sizeThatFits(in: CGSize(width: 343, height: 500))
        XCTAssertLessThan(toastSize.width, 180)
        XCTAssertLessThan(toastSize.height, 60)

        let notice = EInlineNotice(tone: .error) { Text("连接已断开") } actions: {
            HStack(spacing: 0) {
                Button {} label: { Text("重连").frame(minWidth: 44, minHeight: 44) }
                EIconAction(accessibilityLabel: Text("关闭"), action: {}) { Image(systemName: "xmark") }
            }
        }
        let normal = UIHostingController(rootView: notice).sizeThatFits(in: CGSize(width: 343, height: 500))
        let accessible = UIHostingController(rootView: notice.environment(\.dynamicTypeSize, .accessibility3))
            .sizeThatFits(in: CGSize(width: 343, height: 1000))
        XCTAssertLessThanOrEqual(normal.width, 343)
        XCTAssertLessThan(normal.height, 65)
        XCTAssertLessThanOrEqual(accessible.width, 343)
        XCTAssertGreaterThan(accessible.height, normal.height)

        let long = EInlineNotice(tone: .error) {
            Text(verbatim: String(repeating: "Die Verbindung zum Gerät wurde unterbrochen. ", count: 5))
        } actions: {
            Button {} label: { Text("Erneut verbinden").frame(minWidth: 44, minHeight: 44) }
        }
        for width: CGFloat in [288, 343] {
            let size = UIHostingController(rootView: long).sizeThatFits(in: CGSize(width: width, height: 2000))
            XCTAssertLessThanOrEqual(size.width, width)
            XCTAssertGreaterThan(size.height, normal.height)
        }
    }

    func testNoticeCenterDoesNotRetainItselfThroughTimer() {
        weak var reference: ENoticeCenter?
        autoreleasepool {
            let center = ENoticeCenter()
            reference = center
            center.show(.transientSuccess("Saved"))
        }
        XCTAssertNil(reference)
    }

    func testLongFormFitsRequiredWidthsAndGrowsForAccessibility() {
        for width in [375.0, 393.0, 430.0] {
            let normal = measuredForm(width: width, typeSize: .large)
            let accessible = measuredForm(width: width, typeSize: .accessibility3)
            XCTAssertLessThanOrEqual(normal.width, width + 1)
            XCTAssertLessThanOrEqual(accessible.width, width + 1)
            XCTAssertGreaterThan(accessible.height, normal.height)
        }
    }

    private func measuredForm(width: CGFloat, typeSize: DynamicTypeSize) -> CGSize {
        let view = VStack {
            EField(error: Text("A long validation error remains readable and does not discard the current value.")) {
                Text("A long field title that must remain readable")
            } content: {
                ETextField(Text("Title"), text: .constant("  original text  "), isInvalid: true)
            }
            ESettingsRow(detail: Text("A long explanation that grows with the preferred text size")) {
                Text("Preference")
            } content: {
                ESwitch(isOn: .constant(true)) { Text("Enabled") }
            }
        }
        .environment(\.dynamicTypeSize, typeSize)
        let host = UIHostingController(rootView: view)
        return host.sizeThatFits(in: CGSize(width: width, height: .greatestFiniteMagnitude))
    }
}

#endif
