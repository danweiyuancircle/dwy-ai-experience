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

    func testAlertDismissesAndCanReopenWithLocalizedText() {
        for (language, title, dismiss) in [("en", "Information", "Got it"), ("zh-Hans", "提示", "知道了")] {
            launchDialogs(language: language)
            for _ in 0..<2 {
                app.buttons["showcase.alert"].tap()
                let alert = app.alerts.firstMatch
                XCTAssertTrue(alert.waitForExistence(timeout: 3))
                XCTAssertTrue(alert.staticTexts[title].exists)
                let attachment = XCTAttachment(screenshot: app.screenshot())
                attachment.name = "alert-\(language)"
                attachment.lifetime = .keepAlways
                add(attachment)
                alert.buttons[dismiss].tap()
                XCTAssertTrue(alert.waitForNonExistence(timeout: 3))
                XCTAssertEqual(app.staticTexts["showcase.alertPresented"].value as? String, "false")
            }
        }
    }

    func testConfirmCancelDoesNotPerformActionAndConfirmRunsOnce() {
        launchDialogs()
        let trigger = app.buttons["showcase.confirm"]
        let count = app.staticTexts["showcase.confirmCount"]
        trigger.tap()
        let alert = app.alerts.firstMatch
        XCTAssertTrue(alert.waitForExistence(timeout: 3))
        XCTAssertEqual(count.value as? String, "0")
        alert.buttons["Cancel"].tap()
        XCTAssertTrue(alert.waitForNonExistence(timeout: 3))
        XCTAssertEqual(count.value as? String, "0")
        trigger.tap()
        XCTAssertTrue(alert.waitForExistence(timeout: 3))
        let attachment = XCTAttachment(screenshot: app.screenshot())
        attachment.name = "destructive-confirm"
        attachment.lifetime = .keepAlways
        add(attachment)
        alert.buttons["Delete"].tap()
        XCTAssertTrue(alert.waitForNonExistence(timeout: 3))
        XCTAssertEqual(count.value as? String, "1")
        XCTAssertEqual(app.staticTexts["showcase.confirmPresented"].value as? String, "false")
        trigger.tap()
        XCTAssertTrue(alert.waitForExistence(timeout: 3))
        alert.buttons["Delete"].tap()
        XCTAssertTrue(alert.waitForNonExistence(timeout: 3))
        XCTAssertEqual(count.value as? String, "2")
    }

    func testErrorAlertPreservesRawMessageAndClearsBindingOnDismiss() {
        launchDialogs()
        let state = app.staticTexts["showcase.errorPresent"]
        XCTAssertEqual(state.value as? String, "false")
        for _ in 0..<2 {
            app.buttons["showcase.errorAlert"].tap()
            let alert = app.alerts.firstMatch
            XCTAssertTrue(alert.waitForExistence(timeout: 3))
            XCTAssertTrue(alert.staticTexts["server.error.key"].exists)
            alert.buttons["Got it"].tap()
            XCTAssertTrue(alert.waitForNonExistence(timeout: 3))
            XCTAssertEqual(state.value as? String, "false")
        }
    }

    private func launchDialogs(language: String = "en") {
        app.terminate()
        app.launchArguments = ["--dialogs-preview", "-AppleLanguages", "(\(language))"]
        app.launch()
        XCTAssertTrue(app.buttons["showcase.alert"].waitForExistence(timeout: 5))
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
