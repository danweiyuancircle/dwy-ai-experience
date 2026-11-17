#if os(macOS)
import XCTest
@testable import PermissionMac
@testable import PermissionFlow
import AppKit

@MainActor
final class PermissionMacTests: XCTestCase {
    func testSwitchingToCameraClosesExistingFloatingGuide() {
        _ = NSApplication.shared
        let controller = PermissionFlowController(openSettings: { _ in true })
        controller.showPanel()
        defer { controller.closePanel() }
        XCTAssertTrue(controller.authorize(pane: .camera))
        XCTAssertFalse(NSApplication.shared.windows.contains { $0 is FloatingDropPanel && $0.isVisible })
    }

    func testRejectedSettingsNavigationClosesGuideAndClearsPane() {
        let controller = PermissionFlowController(openSettings: { _ in false })
        XCTAssertFalse(controller.authorize(pane: .fullDiskAccess))
        XCTAssertNil(controller.currentPane)
    }
    func testDiskAndNetworkCannotClaimGlobalAuthorization() {
        let permissions = MacPermissions()
        XCTAssertEqual(permissions.status(for: .fullDiskAccess), .unknown)
        XCTAssertEqual(permissions.status(for: .localNetwork), .unknown)
        XCTAssertEqual(FullDiskAccessPermissionStatusProvider().capability, .unsupported)
        XCTAssertEqual(FullDiskAccessPermissionStatusProvider().authorizationState(), .unknown)
    }

    func testNativeStatesPreserveRestrictionsAndWriteOnly() {
        XCTAssertEqual(MacPermissions.captureState(.restricted), .restricted)
        XCTAssertEqual(MacPermissions.captureState(.notDetermined), .notDetermined)
        XCTAssertEqual(MacPermissions.eventState(.writeOnly), .writeOnly)
    }

    func testGuidanceOnlyPermissionNeverClaimsRequestSuccess() async {
        do { _ = try await MacPermissions().request(.fullDiskAccess); XCTFail() }
        catch MacPermissionError.requiresSystemSettings(.fullDiskAccess) {}
        catch { XCTFail("\(error)") }
    }
}
#endif
