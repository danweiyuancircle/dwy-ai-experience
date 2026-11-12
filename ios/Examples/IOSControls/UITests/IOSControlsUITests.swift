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

    private func reveal(_ element: XCUIElement, file: StaticString = #filePath, line: UInt = #line) {
        let scrollView = app.scrollViews.firstMatch
        for _ in 0..<12 {
            if element.exists && element.isHittable { return }
            scrollView.swipeUp()
        }
        XCTFail("Showcase element did not become hittable: \(element.identifier)", file: file, line: line)
    }
}
