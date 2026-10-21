import XCTest
@testable import L10nKit

final class L10nKitTests: XCTestCase {
    func testAppLanguageCodes() {
        XCTAssertNil(AppLanguage.system.code)
        XCTAssertEqual(AppLanguage.zhHans.code, "zh-Hans")
        XCTAssertEqual(AppLanguage.en.code, "en")
        XCTAssertFalse(AppLanguage.resourceLanguages.contains(.system))
    }

    func testResolveSystemCodeEnglish() {
        // 不依赖真实系统语言：直接测映射辅助逻辑的输入侧等价——supported 含 en。
        let code = LocalizationManager.resolveSystemCode(supportedCodes: ["zh-Hans", "en"])
        XCTAssertTrue(["zh-Hans", "en"].contains(code))
    }

    func testResolvePrefersSupportedFirstFallback() {
        let code = LocalizationManager.resolveSystemCode(supportedCodes: ["ja", "ko"])
        XCTAssertTrue(["ja", "ko"].contains(code))
    }

    func testLocOnMainThreadDoesNotCrash() {
        // 缺 lproj 时回退 key 或 main bundle，重点是 trackLanguageAccess 不炸。
        _ = loc("language_system")
    }
}
