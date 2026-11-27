#if os(macOS)
import AppKit
import DesignKitMac
import SwiftUI
import XCTest
@testable import BusinessKitMac

@MainActor
final class BusinessSettingsRowsTests: XCTestCase {
    private func fittingSize<V: View>(_ view: V, width: CGFloat = 480) -> CGSize {
        _ = NSApplication.shared
        return NSHostingView(rootView: view.frame(width: width)).fittingSize
    }

    func testRowsFillTheProposedWidthAndKeepAReadableHeight() {
        var isOn = true
        let binding = Binding(get: { isOn }, set: { isOn = $0 })
        let rows: [AnyView] = [
            AnyView(BusinessInfoRow(systemImage: "info.circle", title: Text(verbatim: "Version"), value: Text(verbatim: "1.0"))),
            AnyView(BusinessToggleRow(systemImage: "ladybug", title: Text(verbatim: "Debug"),
                                       detail: Text(verbatim: "Show extra diagnostics"), isOn: binding)),
            AnyView(BusinessNavRow(systemImage: "envelope", title: Text(verbatim: "Feedback"),
                                    detail: Text(verbatim: "Email, Discord"), action: {})),
            AnyView(BusinessMenuRow(systemImage: "globe", title: Text(verbatim: "Language")) {
                Text(verbatim: "English")
            }),
        ]
        for row in rows {
            let size = fittingSize(row)
            XCTAssertEqual(size.width, 480, accuracy: 1)
            XCTAssertGreaterThanOrEqual(size.height, 28)
            XCTAssertLessThan(size.height, 80)
        }
    }

    func testGroupSeparatesRowsWithAnInsetDividerButNotAroundThem() {
        let one = BusinessSettingsGroup {
            BusinessInfoRow(systemImage: "info.circle", title: Text(verbatim: "A"), value: Text(verbatim: "1"))
        }
        let three = BusinessSettingsGroup {
            BusinessInfoRow(systemImage: "info.circle", title: Text(verbatim: "A"), value: Text(verbatim: "1"))
            BusinessInfoRow(systemImage: "info.circle", title: Text(verbatim: "B"), value: Text(verbatim: "2"))
            BusinessInfoRow(systemImage: "info.circle", title: Text(verbatim: "C"), value: Text(verbatim: "3"))
        }
        let singleHeight = fittingSize(one).height
        let tripleHeight = fittingSize(three).height
        // 三行比单行高出至少两行高度，说明每行都被渲染；分隔线只在行间出现。
        XCTAssertGreaterThan(tripleHeight, singleHeight + 2 * 28)
        XCTAssertLessThan(tripleHeight, 3 * singleHeight)
    }

    func testGroupHidesConditionalRowsWithoutLeavingDividers() {
        let show = false
        let group = BusinessSettingsGroup {
            BusinessInfoRow(systemImage: "info.circle", title: Text(verbatim: "A"), value: Text(verbatim: "1"))
            if show {
                BusinessInfoRow(systemImage: "info.circle", title: Text(verbatim: "B"), value: Text(verbatim: "2"))
            }
        }
        let single = BusinessSettingsGroup {
            BusinessInfoRow(systemImage: "info.circle", title: Text(verbatim: "A"), value: Text(verbatim: "1"))
        }
        XCTAssertEqual(fittingSize(group).height, fittingSize(single).height, accuracy: 1)
    }
}
#endif
