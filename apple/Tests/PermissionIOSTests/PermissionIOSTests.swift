#if os(iOS)
import XCTest
import PermissionCore
import PermissionIOS
import PermissionCameraIOS
import PermissionPhotoLibraryIOS
import PermissionMicrophoneIOS
import PermissionContactsIOS
import PermissionSpeechIOS
import PermissionMotionIOS
import PermissionMediaLibraryIOS
import PermissionBluetoothIOS
import PermissionTrackingIOS
import PermissionSiriIOS
import PermissionCalendarIOS
import PermissionRemindersIOS
@testable import PermissionNotificationIOS
@testable import PermissionLocationIOS
import CoreLocation
import PermissionHealthIOS
import PermissionFaceIDIOS

@MainActor
final class PermissionIOSTests: XCTestCase {
    func testExplicitNotificationRequestCanUpgradeProvisional() {
        XCTAssertTrue(notificationRequestableStates(options: [.alert, .badge, .sound]).contains(.provisional))
        XCTAssertFalse(notificationRequestableStates(options: [.provisional]).contains(.provisional))
    }

    func testAlwaysUpgradeDoesNotWaitForUnchangedAuthorization() async throws {
        let manager = UnchangedLocationManager()
        let permission = LocationPermission(manager: manager, validateUsageDescriptions: { _ in })
        let task = Task { try await permission.request(always: true) }
        await Task.yield()
        task.cancel()
        let state = try await task.value
        XCTAssertEqual(state, .whenInUse)
        XCTAssertEqual(manager.upgrades, 1)
    }
    func testPermissionFactoriesDoNotRequestAuthorization() {
        XCTAssertEqual(IOSPermissions.camera.id, "ios.camera")
        XCTAssertEqual(IOSPermissions.photoLibrary.id, "ios.photoLibrary")
        XCTAssertEqual(IOSPermissions.calendar(access: .full).id, "ios.calendar.full")
        XCTAssertNotEqual(IOSPermissions.calendar(access: .full).id, IOSPermissions.calendar(access: .writeOnly).id)
    }

    func testMissingUsageDescriptionIsReportedBeforeSystemRequest() {
        XCTAssertThrowsError(try IOSPermissions.validateUsageDescriptions(["DWYMissingPermissionDescription"])) { error in
            XCTAssertEqual(error as? IOSPermissionError, .missingUsageDescription("DWYMissingPermissionDescription"))
        }
    }

    func testAuthenticationRequiresMeaningfulReason() async {
        do { _ = try await IOSPermissions.authenticateWithBiometrics(reason: "  "); XCTFail() }
        catch IOSPermissionError.emptyAuthenticationReason {}
        catch { XCTFail("\(error)") }
    }
}

@MainActor
private final class UnchangedLocationManager: CLLocationManager {
    var upgrades = 0
    override var authorizationStatus: CLAuthorizationStatus { .authorizedWhenInUse }
    override func requestAlwaysAuthorization() { upgrades += 1 }
}
#endif
