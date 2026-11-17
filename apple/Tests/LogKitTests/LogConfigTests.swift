import XCTest
@testable import LogKit

final class LogConfigTests: XCTestCase {
    func testDefaultMinimumLevelMatchesBuildConfiguration() {
        #if DEBUG
        XCTAssertEqual(LogConfig.defaultMinimumLevel, .debug)
        XCTAssertTrue(LogConfig.defaultAlsoLogToConsole)
        #else
        XCTAssertEqual(LogConfig.defaultMinimumLevel, .info)
        XCTAssertFalse(LogConfig.defaultAlsoLogToConsole)
        #endif
    }

    func testAppFactory() {
        let cfg = LogConfig.app(subsystem: "com.example.demo", fileName: "demo.log")
        XCTAssertEqual(cfg.subsystem, "com.example.demo")
        XCTAssertEqual(cfg.fileName, "demo.log")
        XCTAssertTrue(cfg.directoryURL.path.contains("com.example.demo"))
        XCTAssertEqual(cfg.maxFileSizeBytes, 2 * 1024 * 1024)
        XCTAssertEqual(cfg.maxArchivedFilesCount, 5)
    }

    func testMaxArchivedClamped() {
        XCTAssertEqual(LogConfig(subsystem: "t", maxArchivedFilesCount: -3).maxArchivedFilesCount, 0)
        XCTAssertEqual(LogConfig(subsystem: "t", maxArchivedFilesCount: 999).maxArchivedFilesCount, 255)
    }

    func testAppLogLevelOrdering() {
        XCTAssertTrue(AppLogLevel.debug < .info)
        XCTAssertTrue(AppLogLevel.info < .warn)
        XCTAssertTrue(AppLogLevel.warn < .error)
        XCTAssertEqual(AppLogLevel.warn.token, "WARN")
    }
}
