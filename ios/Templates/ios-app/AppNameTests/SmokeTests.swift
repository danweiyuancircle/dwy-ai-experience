import XCTest
@testable import __APP_NAME__

final class SmokeTests: XCTestCase {
    func testBundleLoads() {
        XCTAssertNotNil(Bundle.main.bundleIdentifier)
    }
}
