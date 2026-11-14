import XCTest

final class IOSControlsUITests: XCTestCase {
    private var app: XCUIApplication!

    override func setUpWithError() throws {
        continueAfterFailure = false
        app = XCUIApplication()
        app.launch()
    }

    func testTextInputUpdatesVisibleBindingWithoutTrimming() {
        let field = app.textFields["showcase.name"]
        reveal(field)
        field.tap()
        XCTAssertTrue(app.keyboards.firstMatch.waitForExistence(timeout: 5))
        field.typeText("  sample  ")
        XCTAssertEqual(field.value as? String, "  sample  ")
        let boundValue = app.staticTexts["showcase.nameValue"]
        XCTAssertTrue(boundValue.waitForExistence(timeout: 3))
        XCTAssertEqual(boundValue.label, "  sample  ")
    }

    func testSegmentSelectionWritesBinding() {
        let control = app.segmentedControls["showcase.segment"]
        reveal(control)
        let second = control.buttons.element(boundBy: 1)
        second.tap()
        XCTAssertTrue(second.isSelected)
        XCTAssertEqual(app.staticTexts["showcase.segmentValue"].value as? String, "1")
        control.buttons.element(boundBy: 0).tap()
        XCTAssertEqual(app.staticTexts["showcase.segmentValue"].value as? String, "0")
    }

    func testFullWidthPrimaryActionEdgesEachTriggerOnce() {
        let button = app.buttons["showcase.primary"]
        reveal(button)
        XCTAssertGreaterThan(button.frame.width, app.frame.width * 0.65)
        button.coordinate(withNormalizedOffset: CGVector(dx: 0.03, dy: 0.5)).tap()
        let count = app.staticTexts["showcase.actionCount"]
        XCTAssertEqual(count.value as? String, "1")
        button.coordinate(withNormalizedOffset: CGVector(dx: 0.97, dy: 0.5)).tap()
        XCTAssertEqual(count.value as? String, "2")
        XCTAssertTrue(button.isEnabled)
    }

    func testFeedbackToastAndCompactPersistentNotice() {
        app.terminate()
        for dark in [false, true] {
            app.launchArguments = ["--feedback-preview", "-AppleLanguages", "(zh-Hans)"]
            if dark { app.launchArguments.append("--feedback-dark") }
            app.launch()
            let copy = app.buttons["showcase.copyNotice"]
            XCTAssertTrue(copy.waitForExistence(timeout: 5))
            copy.tap()
            let toast = app.descendants(matching: .any)["notice.toast"].firstMatch
            XCTAssertTrue(toast.exists, app.debugDescription)
            let copied = XCTAttachment(screenshot: app.screenshot())
            copied.name = dark ? "feedback-toast-dark" : "feedback-toast-light"
            copied.lifetime = .keepAlways
            add(copied)
            XCTAssertTrue(toast.waitForNonExistence(timeout: 3))

            app.buttons["showcase.persistentNotice"].tap()
            let retry = app.buttons["showcase.retryNotice"]
            XCTAssertTrue(retry.waitForExistence(timeout: 2))
            XCTAssertGreaterThanOrEqual(retry.frame.height, 44)
            let persistent = XCTAttachment(screenshot: app.screenshot())
            persistent.name = dark ? "feedback-persistent-dark" : "feedback-persistent-light"
            persistent.lifetime = .keepAlways
            add(persistent)
            XCTAssertFalse(retry.waitForNonExistence(timeout: 2))
            retry.tap()
            XCTAssertTrue(retry.waitForNonExistence(timeout: 2))
            app.terminate()
        }
    }

    private func reveal(_ element: XCUIElement, file: StaticString = #filePath, line: UInt = #line) {
        let scrollView = app.scrollViews.firstMatch
        for _ in 0..<12 {
            if element.exists && element.isHittable { return }
            scrollView.swipeUp()
        }
        XCTFail("Showcase element did not become hittable: \(element.identifier)", file: file, line: line)
    }
}
