#if os(macOS)
import Foundation
import XCTest
@testable import BusinessKitMac

final class SupportTests: XCTestCase {
    func testHelpDocumentAndContactUseSeparateURLPolicies() throws {
        let web = try XCTUnwrap(URL(string: "https://example.com/help"))
        let email = try XCTUnwrap(URL(string: "mailto:help@example.com"))
        let script = try XCTUnwrap(URL(string: "javascript:example()"))
        XCTAssertTrue(SupportLink.canRead(web))
        XCTAssertTrue(SupportLink.canOpen(email))
        XCTAssertFalse(SupportLink.canRead(email))
        XCTAssertFalse(SupportLink.canOpen(script))
        XCTAssertFalse(SupportLink.canRead(URL(fileURLWithPath: "/example")))
    }

    func testExportRejectsNamesThatCanEscapeItsTemporaryDirectory() {
        for name in ["", "..", "../image.png", "/image.png", "my:photo.png"] {
            XCTAssertThrowsError(try PreparedSupportFile.prepare(.data(Data()), fileName: name))
        }
    }

    func testLogExportRequiresAnApplicationLogDirectory() {
        XCTAssertThrowsError(try PreparedSupportFile.exportLogs(fileNamePrefix: "BusinessKitMacTests")) { error in
            guard let failure = error as? SupportFileError, case .noLogs = failure else {
                return XCTFail("Expected app log initialization error, got \(error)")
            }
        }
    }

    func testGeneratedAndBorrowedFileLifetimesAreSeparate() throws {
        let data = Data([1, 2, 3])
        let generated = try PreparedSupportFile.prepare(.data(data), fileName: "preview.png")
        defer { generated.cleanUp() }
        let destination = try PreparedSupportFile.prepare(.data(Data([4])), fileName: "old.png")
        defer { destination.cleanUp() }

        let borrowed = try PreparedSupportFile.prepare(.file(generated.url), fileName: "new.png")
        try borrowed.save(to: destination.url)
        borrowed.cleanUp()
        XCTAssertEqual(try Data(contentsOf: generated.url), data)
        XCTAssertEqual(try Data(contentsOf: destination.url), data)

        generated.cleanUp()
        XCTAssertFalse(FileManager.default.fileExists(atPath: generated.url.path))
        XCTAssertTrue(FileManager.default.fileExists(atPath: destination.url.path))
    }
}
#endif
