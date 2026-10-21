import XCTest
@testable import BizFoundation

final class BizFoundationTests: XCTestCase {
    func testReady() {
        XCTAssertTrue(DomainFacade.ready)
        XCTAssertEqual(DomainFacade.formatDemoSeconds(65), "01:05")
    }

    func testReviewGatePromptsOnlyOnThirdLaunch() {
        XCTAssertFalse(ReviewGate.shouldPrompt(launchCount: 1))
        XCTAssertFalse(ReviewGate.shouldPrompt(launchCount: 2))
        XCTAssertTrue(ReviewGate.shouldPrompt(launchCount: 3))
        XCTAssertFalse(ReviewGate.shouldPrompt(launchCount: 4))
        XCTAssertFalse(ReviewGate.shouldPrompt(launchCount: 6))
    }

    func testWriteReviewURLNilUntilAppStoreIDFilled() {
        XCTAssertNil(AppConfig.writeReviewURL)
    }

    func testPrivacyURLFollowsChineseLocale() {
        XCTAssertEqual(AppConfig.privacyURL(localeIdentifier: "zh-Hans"), AppConfig.privacyURLZh)
        XCTAssertEqual(AppConfig.privacyURL(localeIdentifier: "en"), AppConfig.privacyURLEn)
    }

    func testFeedbackMailtoEncodesSubjectAndTargetsInbox() {
        let url = AppConfig.feedbackMailtoURL(
            subject: "EasyJPG 意见反馈",
            body: "\n\n---\nEasyJPG 1.0 (1)\n"
        )
        XCTAssertNotNil(url)
        XCTAssertEqual(url?.scheme, "mailto")
        XCTAssertTrue(url?.absoluteString.hasPrefix("mailto:tianxiake1994@gmail.com") == true)
        XCTAssertTrue(url?.absoluteString.contains("subject=") == true)
        XCTAssertTrue(url?.absoluteString.contains("%") == true)
    }
}
