#if os(macOS)
import XCTest
import SwiftUI
import AppKit
import DesignKitMac
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
            let source = root.appendingPathComponent("apple/Sources/macOS/edesign-kit-mac-playground/Fixtures/\(component.fixtureName).swift")
            let actual = try String(contentsOf: source, encoding: .utf8)
            let document = try EPlaygroundCatalog.documentation(for: component, locale: Locale(identifier: "en"))
            XCTAssertEqual(document.swift, actual, component.id)
        }
    }

    func testCatalogCoversEveryPublicMacVisualComponent() throws {
        let directory = repositoryRoot.appendingPathComponent("apple/Sources/macOS/edesign-kit")
        let regex = try NSRegularExpression(pattern: #"public struct (E\w+)(?:<[^\n]+>)?: View\b"#)
        // The list style has a visual fixture even though it is applied as a modifier.
        var symbols: Set<String> = ["EManagementListStyle"]
        for url in try FileManager.default.contentsOfDirectory(at: directory, includingPropertiesForKeys: nil) where url.pathExtension == "swift" {
            let source = try String(contentsOf: url, encoding: .utf8)
            let text = source as NSString
            for match in regex.matches(in: source, range: NSRange(location: 0, length: text.length)) {
                symbols.insert(text.substring(with: match.range(at: 1)))
            }
        }
        XCTAssertEqual(Set(EPlaygroundComponent.allCases.map(\.symbol)), symbols)
    }

    func testEveryComponentListsStructuredCapabilitiesInBothLanguages() throws {
        for component in EPlaygroundComponent.allCases {
            for language in ["en", "zh-Hans"] {
                let document = try EPlaygroundCatalog.documentation(for: component, locale: Locale(identifier: language))
                XCTAssertGreaterThanOrEqual(document.capabilities.count, 2, "\(component.id) \(language)")
                for capability in document.capabilities {
                    XCTAssertFalse(capability.title.isEmpty, "\(component.id) \(language)")
                    XCTAssertFalse(capability.detail.isEmpty, "\(component.id) \(language)")
                }
            }
            let english = try EPlaygroundCatalog.documentation(for: component, locale: Locale(identifier: "en"))
            let chinese = try EPlaygroundCatalog.documentation(for: component, locale: Locale(identifier: "zh-Hans"))
            XCTAssertEqual(english.capabilities.count, chinese.capabilities.count, component.id)
        }
    }

    func testTokenValuesComeFromTheInjectedTheme() {
        var theme = EControlTheme()
        theme.spacing.group = 16
        theme.fieldRadius = 10
        theme.fieldHeight = 32
        XCTAssertEqual(EPlaygroundTokens.spacing(theme).first { $0.name == "group" }?.value, 16)
        XCTAssertEqual(EPlaygroundTokens.spacing(theme).count, 8)
        XCTAssertEqual(EPlaygroundTokens.radii(theme).first { $0.name == "fieldRadius" }?.value, 10)
        XCTAssertEqual(EPlaygroundTokens.controlSizes(theme).first { $0.name == "fieldHeight" }?.value, 32)
        XCTAssertEqual(EPlaygroundTokens.colors(theme.colors).count, 16)
        XCTAssertEqual(ETextRole.allCases.count, 7)
    }

    @MainActor
    func testTokenColorsResolveForTheRequestedScheme() {
        let background = EControlTheme.standard.colors.background
        XCTAssertEqual(EPlaygroundTokens.hex(background, scheme: .light), "#FAFAFA")
        XCTAssertEqual(EPlaygroundTokens.hex(background, scheme: .dark), "#0A0A0B")
    }

    func testLaunchArgumentsSelectPageAppearanceScenarioAndLanguage() {
        let launch = EPlaygroundLaunch(arguments: ["app", "--page", "designkit.mac.button", "--appearance", "dark",
                                                   "--scenario", "Busy", "--language", "zh-Hans"])
        XCTAssertEqual(launch.component, .button)
        XCTAssertFalse(launch.showsTokens)
        XCTAssertEqual(launch.options.appearance, 2)
        XCTAssertEqual(launch.options.language, 2)
        XCTAssertEqual(launch.scenario, .busy)
        XCTAssertTrue(EPlaygroundLaunch(arguments: ["--page", "tokens"]).showsTokens)
        let unknown = EPlaygroundLaunch(arguments: ["--page", "nope", "--appearance", "sepia"])
        XCTAssertNil(unknown.component)
        XCTAssertFalse(unknown.showsTokens)
        XCTAssertEqual(unknown.options, EPreviewOptions())
        XCTAssertNil(EPlaygroundLaunch(arguments: ["--page"]).component)
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
