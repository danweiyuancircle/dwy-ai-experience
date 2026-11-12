#if os(macOS)
import XCTest
import SwiftUI
import AppKit
@testable import DesignKitMacPlayground

final class EPlaygroundCatalogTests: XCTestCase {
    func testStableIdentitiesAndBilingualResourcesAreComplete() throws {
        let components = EPlaygroundComponent.allCases
        XCTAssertEqual(Set(components.map(\.id)).count, components.count)
        for component in components {
            XCTAssertTrue(component.id.hasPrefix("designkit.mac."))
            let english = try EPlaygroundCatalog.documentation(for: component, locale: Locale(identifier: "en"))
            let chinese = try EPlaygroundCatalog.documentation(for: component, locale: Locale(identifier: "zh-Hans"))
            XCTAssertEqual(english.swift, chinese.swift)
            XCTAssertTrue(english.swift.contains("struct \(component.fixtureName): View"))
            XCTAssertTrue(english.swift.contains("import DesignKitMac"))
            XCTAssertTrue(english.markdown.contains(component.id))
            XCTAssertTrue(chinese.markdown.contains("## 用途"))
            XCTAssertTrue(english.markdown.contains("## Purpose"))
            XCTAssertNotEqual(english.markdown, chinese.markdown)
            XCTAssertFalse(english.summary.contains("\n"))
            XCTAssertFalse(chinese.summary.contains("##"))
            XCTAssertTrue(english.markdown.contains(english.summary))
            XCTAssertTrue(chinese.markdown.contains(chinese.summary))
        }
    }

    func testCopiedCodeMatchesCompiledFixtureExactly() throws {
        let root = repositoryRoot
        for component in EPlaygroundComponent.allCases {
            let source = root.appendingPathComponent("ios/Sources/macOS/DesignKitMacPlayground/Fixtures/\(component.fixtureName).swift")
            let actual = try String(contentsOf: source, encoding: .utf8)
            let document = try EPlaygroundCatalog.documentation(for: component, locale: Locale(identifier: "en"))
            XCTAssertEqual(document.swift, actual, component.id)
        }
    }

    func testCatalogCoversEveryPublicMacVisualComponent() throws {
        let directory = repositoryRoot.appendingPathComponent("ios/Sources/macOS/DesignKit")
        let regex = try NSRegularExpression(pattern: #"public struct (E\w+)(?:<[^\n]+>)?: View"#)
        var symbols: Set<String> = []
        for url in try FileManager.default.contentsOfDirectory(at: directory, includingPropertiesForKeys: nil) where url.pathExtension == "swift" {
            let source = try String(contentsOf: url, encoding: .utf8)
            let text = source as NSString
            for match in regex.matches(in: source, range: NSRange(location: 0, length: text.length)) {
                symbols.insert(text.substring(with: match.range(at: 1)))
            }
        }
        XCTAssertEqual(Set(EPlaygroundComponent.allCases.map(\.symbol)), symbols)
    }

    func testSearchIncludesStableIDAndSymbol() {
        XCTAssertTrue(EPlaygroundComponent.secureField.matches("secure"))
        XCTAssertTrue(EPlaygroundComponent.comboBox.matches("designkit.mac.combo-box"))
        XCTAssertFalse(EPlaygroundComponent.button.matches("checkbox"))
    }

    func testPreviewSettingsInheritByDefaultAndResetWithoutChangingHostState() {
        var options = EPreviewOptions()
        XCTAssertNil(options.scheme)
        XCTAssertNil(options.locale)
        XCTAssertNil(options.controlPlacement)
        options.appearance = 2
        options.language = 2
        options.largeText = true
        options.placement = 3
        XCTAssertTrue(options.scheme == .dark)
        XCTAssertEqual(options.locale?.identifier, "zh-Hans")
        XCTAssertTrue(options.controlPlacement == .floating)
        options = EPreviewOptions()
        XCTAssertNil(options.scheme)
        XCTAssertNil(options.locale)
        XCTAssertNil(options.controlPlacement)
        XCTAssertFalse(options.largeText)
    }

    @MainActor
    func testEveryRenderedExampleHasReadableLayoutAtTwoWidths() {
        for width: CGFloat in [420, 700] {
            for component in EPlaygroundComponent.allCases {
                for scenario in component.scenarios {
                    let host = NSHostingView(rootView: EPlaygroundFixture(component: component, scenario: scenario).frame(width: width))
                    let size = host.fittingSize
                    XCTAssertGreaterThan(size.height, 0, "\(component.id) \(scenario)")
                    XCTAssertTrue(size.height.isFinite)
                    XCTAssertLessThanOrEqual(size.width, width + 1)
                }
            }
        }
    }

    @MainActor
    func testPublicPlaygroundAcceptsOptionalHostComposition() {
        let standalone = NSHostingView(rootView: EPlayground().frame(width: 1000, height: 700))
        let project = NSHostingView(rootView: EPlayground(projectTitle: Text("Project")) {
            Text("Host-owned composition")
        }.frame(width: 1000, height: 700))
        XCTAssertGreaterThan(standalone.fittingSize.width, 0)
        XCTAssertGreaterThan(project.fittingSize.height, 0)
    }

    private var repositoryRoot: URL {
        URL(fileURLWithPath: #filePath).deletingLastPathComponent()
            .deletingLastPathComponent().deletingLastPathComponent().deletingLastPathComponent()
    }
}
#endif
