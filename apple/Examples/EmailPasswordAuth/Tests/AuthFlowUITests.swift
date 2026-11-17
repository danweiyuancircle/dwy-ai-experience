import XCTest

@MainActor
final class AuthFlowUITests: XCTestCase {
    func testInitialPresentationAndRegistrationNavigation() {
        let app = XCUIApplication()
        app.launch()
        XCTAssertTrue(app.textFields["auth.email"].waitForExistence(timeout: 8))
        app.buttons["auth.goRegister"].tap()
        XCTAssertTrue(app.textFields["auth.code"].exists)
        XCTAssertTrue(app.buttons["auth.sendCode"].exists)
        app.buttons["auth.goLogin"].tap()
        app.buttons["auth.goReset"].tap()
        XCTAssertTrue(app.textFields["auth.code"].exists)
        XCTAssertTrue(app.buttons["auth.goLogin"].exists)
        app.buttons["auth.goLogin"].tap()
        app.buttons["auth.submit"].tap()
        XCTAssertTrue(app.staticTexts["请输入有效的邮箱地址。"].exists)
    }
}
