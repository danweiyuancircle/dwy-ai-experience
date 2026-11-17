import XCTest
@testable import CoreKit

final class CoreKitTests: XCTestCase {
    func testByteCountCompact() {
        XCTAssertEqual(ByteCount.compact(UInt32(560)), "560B")
        XCTAssertEqual(ByteCount.compact(UInt32(200 * 1024)), "200K")
        XCTAssertEqual(ByteCount.compact(UInt64(0)), "0B")
    }

    func testTimeFormatMmss() {
        XCTAssertEqual(TimeFormat.mmss(0), "00:00")
        XCTAssertEqual(TimeFormat.mmss(65), "01:05")
        XCTAssertEqual(TimeFormat.mmss(25 * 60), "25:00")
        XCTAssertEqual(TimeFormat.mmss(-3), "00:00")
    }

    func testHexData() {
        XCTAssertEqual(Data(hexString: "0a0b")?.count, 2)
        XCTAssertNil(Data(hexString: "0a0"))
        XCTAssertNil(Data(hexString: "zz"))
    }
}
