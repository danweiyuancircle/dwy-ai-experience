import XCTest
@testable import SyncCore

@MainActor
final class SyncLifecycleDriverTests: XCTestCase {
    func testLifecycleAndNetworkRecoveryTriggerOnlyWhileForeground() async {
        var starts = 0, stops = 0
        let driver = SyncLifecycleDriver(onForeground: { starts += 1 }, onBackground: { stops += 1 }, monitorNetwork: false)
        await driver.connectivityChanged(isAvailable: true)
        XCTAssertEqual(starts, 0)
        await driver.foreground()
        XCTAssertEqual(starts, 1)
        await driver.connectivityChanged(isAvailable: true)
        XCTAssertEqual(starts, 1)
        await driver.connectivityChanged(isAvailable: false)
        await driver.connectivityChanged(isAvailable: true)
        XCTAssertEqual(starts, 2)
        await driver.background()
        await driver.connectivityChanged(isAvailable: false)
        await driver.connectivityChanged(isAvailable: true)
        XCTAssertEqual(starts, 2)
        XCTAssertEqual(stops, 1)
        await driver.foreground()
        XCTAssertEqual(starts, 3)
    }

    func testInitialAvailableNetworkTriggersOnlyWhenAlreadyForeground() async {
        var starts = 0
        let driver = SyncLifecycleDriver(onForeground: { starts += 1 }, onBackground: {}, monitorNetwork: false)
        await driver.foreground()
        await driver.connectivityChanged(isAvailable: true)
        XCTAssertEqual(starts, 2)
        await driver.connectivityChanged(isAvailable: true)
        XCTAssertEqual(starts, 2)
    }
}
