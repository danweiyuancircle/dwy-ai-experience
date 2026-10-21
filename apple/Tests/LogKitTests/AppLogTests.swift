import XCTest
@testable import LogKit

final class AppLogTests: XCTestCase {
    private var tempDir: URL!

    override func setUpWithError() throws {
        try super.setUpWithError()
        AppLog.resetForTesting()
        tempDir = FileManager.default.temporaryDirectory
            .appendingPathComponent("LogKitTests-\(UUID().uuidString)", isDirectory: true)
        try FileManager.default.createDirectory(at: tempDir, withIntermediateDirectories: true)
    }

    override func tearDownWithError() throws {
        AppLog.resetForTesting()
        try? FileManager.default.removeItem(at: tempDir)
        tempDir = nil
        try super.tearDownWithError()
    }

    private func makeConfig(minimumLevel: AppLogLevel = .debug) -> LogConfig {
        LogConfig(
            subsystem: "com.dwy.apple-app-kit.tests",
            minimumLevel: minimumLevel,
            directoryURL: tempDir,
            fileName: "app.log",
            alsoLogToConsole: false
        )
    }

    func testBootstrapOnce() {
        XCTAssertTrue(AppLog.bootstrap(config: makeConfig()))
        XCTAssertFalse(AppLog.bootstrap(config: makeConfig(minimumLevel: .error)))
        XCTAssertEqual(AppLog.currentConfig?.minimumLevel, .debug)
    }

    func testWritesToFile() throws {
        XCTAssertTrue(AppLog.bootstrap(config: makeConfig()))
        AppLog.info("hello-logkit-write")
        AppLog.flushForTesting()
        let text = try String(
            contentsOf: tempDir.appendingPathComponent("app.log"),
            encoding: .utf8
        )
        XCTAssertTrue(text.contains("hello-logkit-write"))
        XCTAssertTrue(text.contains("INFO"))
    }

    func testLevelFilterSkipsLower() throws {
        XCTAssertTrue(AppLog.bootstrap(config: makeConfig(minimumLevel: .error)))
        AppLog.info("should-not-appear")
        AppLog.error("must-appear")
        AppLog.flushForTesting()
        let text = try String(
            contentsOf: tempDir.appendingPathComponent("app.log"),
            encoding: .utf8
        )
        XCTAssertFalse(text.contains("should-not-appear"))
        XCTAssertTrue(text.contains("must-appear"))
    }

    func testExportZipIncludesLogFile() throws {
        XCTAssertTrue(AppLog.bootstrap(config: makeConfig()))
        AppLog.info("export-me-\(UUID().uuidString)")
        AppLog.flush()
        let zipURL = try LogExport.exportZip(fileName: LogExport.makeFileName(prefix: "LogKitTest"))
        defer { try? FileManager.default.removeItem(at: zipURL) }
        XCTAssertTrue(FileManager.default.fileExists(atPath: zipURL.path))
        XCTAssertTrue(zipURL.pathExtension == "zip")
        let attrs = try FileManager.default.attributesOfItem(atPath: zipURL.path)
        let size = attrs[.size] as? NSNumber
        XCTAssertNotNil(size)
        XCTAssertGreaterThan(size?.intValue ?? 0, 0)
    }

    func testMakeFileNameContainsPrefixAndDigits() {
        let name = LogExport.makeFileName(prefix: "MyApp", date: Date(timeIntervalSince1970: 1_700_000_000))
        XCTAssertTrue(name.hasPrefix("MyApp-"))
        XCTAssertEqual(name.count, "MyApp-".count + 14)
    }
}
