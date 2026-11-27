import XCTest
@testable import DesignKitIOSPlayground

/// 目录、搜索、文档与示例源码一致性均为平台无关逻辑，可在 macOS 上用 `swift test` 执行。
/// 视图本身仅 iOS 编译，这里不覆盖渲染。
final class IOSPlaygroundCatalogTests: XCTestCase {
    func testStableIdentitiesAreUniqueAndNamespaced() {
        let components = IOSPlaygroundComponent.allCases
        XCTAssertEqual(Set(components.map(\.id)).count, components.count)
        XCTAssertEqual(Set(components.map(\.symbol)).count, components.count)
        for component in components {
            XCTAssertTrue(component.id.hasPrefix("designkit.ios."), component.id)
            XCTAssertEqual(component.module, "DesignKitIOS")
            XCTAssertEqual(component.minimumOS, "iOS 18.0")
            XCTAssertTrue(component.symbol.hasPrefix("E"))
            XCTAssertEqual(component.fixtureName, String(component.symbol.dropFirst()) + "Example")
        }
    }

    func testCatalogCoversEveryPublicIOSVisualComponent() throws {
        let views = try NSRegularExpression(pattern: #"public struct (E\w+)(?:<[^\n]+>)?: (?:View|ViewModifier)\b"#)
        var symbols: Set<String> = []
        for source in try publicSources() {
            let text = source as NSString
            for match in views.matches(in: source, range: NSRange(location: 0, length: text.length)) {
                symbols.insert(text.substring(with: match.range(at: 1)))
            }
        }
        XCTAssertFalse(symbols.isEmpty)
        XCTAssertEqual(Set(IOSPlaygroundComponent.allCases.map(\.symbol)), symbols)
    }

    func testEveryComponentBelongsToExactlyOneNonEmptyCategory() {
        var seen: [String] = []
        for category in IOSPlaygroundCategory.allCases {
            let members = IOSPlaygroundComponent.allCases.filter { $0.category == category }
            XCTAssertFalse(members.isEmpty, category.rawValue)
            seen += members.map(\.id)
            XCTAssertFalse(category.title.en.isEmpty)
            XCTAssertNotEqual(category.title.en, category.title.zh)
        }
        XCTAssertEqual(Set(seen), Set(IOSPlaygroundComponent.allCases.map(\.id)))
        XCTAssertEqual(seen.count, IOSPlaygroundComponent.allCases.count)
    }

    func testDocumentationIsBilingualAndListsCapabilities() {
        for component in IOSPlaygroundComponent.allCases {
            let doc = component.documentation
            for text in [doc.summary] + doc.capabilities + doc.constraints {
                XCTAssertFalse(text.en.isEmpty, component.id)
                XCTAssertFalse(text.zh.isEmpty, component.id)
                XCTAssertNotEqual(text.en, text.zh, component.id)
                XCTAssertFalse(text.en.contains("\n") || text.zh.contains("\n"), component.id)
            }
            XCTAssertGreaterThanOrEqual(doc.capabilities.count, 3, component.id)
            XCTAssertGreaterThanOrEqual(doc.constraints.count, 1, component.id)
        }
    }

    func testTextResolvesChineseOnlyForChineseLocales() {
        let text = IOSPlaygroundText(en: "Reset", zh: "重置")
        XCTAssertEqual(text.resolve(Locale(identifier: "zh-Hans")), "重置")
        XCTAssertEqual(text.resolve(Locale(identifier: "zh_CN")), "重置")
        XCTAssertEqual(text.resolve(Locale(identifier: "en")), "Reset")
        XCTAssertEqual(text.resolve(Locale(identifier: "fr")), "Reset")
    }

    func testSearchMatchesSymbolAndStableIDCaseInsensitively() {
        XCTAssertTrue(IOSPlaygroundComponent.secureField.matches("secure"))
        XCTAssertTrue(IOSPlaygroundComponent.secureField.matches("SECUREFIELD"))
        XCTAssertTrue(IOSPlaygroundComponent.noticeHost.matches("designkit.ios.notice-host"))
        XCTAssertTrue(IOSPlaygroundComponent.button.matches(""))
        XCTAssertTrue(IOSPlaygroundComponent.button.matches("  "))
        XCTAssertFalse(IOSPlaygroundComponent.button.matches("picker"))
        XCTAssertEqual(IOSPlaygroundComponent.allCases.filter { $0.matches("zzz-none") }.count, 0)
    }

    func testTokensDestinationIsSearchableByThemeKeywords() {
        XCTAssertTrue(IOSPlaygroundDestination.tokens.matches(""))
        XCTAssertTrue(IOSPlaygroundDestination.tokens.matches("theme"))
        XCTAssertTrue(IOSPlaygroundDestination.tokens.matches("令牌"))
        XCTAssertFalse(IOSPlaygroundDestination.tokens.matches("button"))
        XCTAssertTrue(IOSPlaygroundDestination.component(.button).matches("EButton"))
        XCTAssertFalse(IOSPlaygroundDestination.component(.button).matches("theme"))
    }

    func testChromeAndAppearanceTitlesAreBilingual() {
        XCTAssertEqual(IOSPlaygroundChrome(locale: Locale(identifier: "zh-Hans"))("Done", "完成"), "完成")
        XCTAssertEqual(IOSPlaygroundChrome(locale: Locale(identifier: "en"))("Done", "完成"), "Done")
        for appearance in IOSPreviewOptions.Appearance.allCases {
            XCTAssertNotEqual(appearance.title.en, appearance.title.zh)
        }
    }

    func testScenariosAlwaysStartNormalAndMatchFixtureParameters() {
        for component in IOSPlaygroundComponent.allCases {
            XCTAssertEqual(component.scenarios.first, .normal, component.id)
            XCTAssertTrue(component.scenarios.contains(.disabled), component.id)
            XCTAssertEqual(Set(component.scenarios).count, component.scenarios.count, component.id)
        }
        XCTAssertTrue(IOSPlaygroundComponent.button.scenarios.contains(.busy))
        XCTAssertTrue(IOSPlaygroundComponent.field.scenarios.contains(.invalid))
        XCTAssertTrue(IOSPlaygroundComponent.picker.scenarios.contains(.empty))
        XCTAssertEqual(Set(IOSPlaygroundComponent.form.scenarios), [.normal, .disabled, .busy, .invalid])
    }

    func testBundledExampleMatchesCompiledFixtureWithoutPlatformGuard() throws {
        let directory = playgroundDirectory.appendingPathComponent("Fixtures")
        for component in IOSPlaygroundComponent.allCases {
            let fixture = try String(
                contentsOf: directory.appendingPathComponent(component.fixtureName + ".swift"), encoding: .utf8)
            let example = try IOSPlaygroundCatalog.exampleSource(for: component)
            XCTAssertEqual(example, IOSPlaygroundCatalog.strippingPlatformGuard(fixture), component.id)
            XCTAssertTrue(example.contains("struct \(component.fixtureName): View"), component.id)
            XCTAssertTrue(example.contains("import DesignKitIOS"), component.id)
            XCTAssertFalse(example.contains("#if os(iOS)"), component.id)
        }
    }

    func testGuardStrippingOnlyRemovesOutermostWrapper() {
        let source = "#if os(iOS)\nimport SwiftUI\n#if DEBUG\nlet a = 1\n#endif\n#endif\n"
        XCTAssertEqual(IOSPlaygroundCatalog.strippingPlatformGuard(source), "import SwiftUI\n#if DEBUG\nlet a = 1\n#endif\n")
        XCTAssertEqual(IOSPlaygroundCatalog.strippingPlatformGuard("let b = 2\n"), "let b = 2\n")
    }

    /// 没有 iOS SDK 时不能编译 fixture；至少保证示例引用的 E* 符号都是 DesignKitIOS 真实公开的类型。
    func testFixturesReferenceOnlyPublicDesignKitIOSSymbols() throws {
        let declaration = try NSRegularExpression(pattern: #"public (?:struct|enum|final class|class) (E\w+)"#)
        var publicSymbols: Set<String> = []
        for source in try publicSources() {
            let text = source as NSString
            for match in declaration.matches(in: source, range: NSRange(location: 0, length: text.length)) {
                publicSymbols.insert(text.substring(with: match.range(at: 1)))
            }
        }
        let usage = try NSRegularExpression(pattern: #"\bE[A-Z]\w*"#)
        let allowedLocal: Set<String> = []
        for component in IOSPlaygroundComponent.allCases {
            let example = try IOSPlaygroundCatalog.exampleSource(for: component)
            let text = example as NSString
            let used = Set(usage.matches(in: example, range: NSRange(location: 0, length: text.length))
                .map { text.substring(with: $0.range) })
            XCTAssertTrue(used.contains(component.symbol), "\(component.id) must demonstrate \(component.symbol)")
            XCTAssertTrue(used.subtracting(allowedLocal).isSubset(of: publicSymbols),
                          "\(component.id): \(used.subtracting(publicSymbols))")
        }
    }

    func testPreviewOptionsInheritByDefaultAndResetRestoresDefaults() {
        var options = IOSPreviewOptions()
        XCTAssertTrue(options.isDefault)
        XCTAssertEqual(options.appearance, .system)
        XCTAssertFalse(options.largeText)
        XCTAssertFalse(options.alternateBrand)
        XCTAssertFalse(options.floatingPlacement)
        options.appearance = .dark
        options.largeText = true
        options.alternateBrand = true
        options.floatingPlacement = true
        XCTAssertFalse(options.isDefault)
        options.reset()
        XCTAssertEqual(options, IOSPreviewOptions())
    }

    private var playgroundDirectory: URL {
        repositoryRoot.appendingPathComponent("apple/Sources/iOS/edesign-kit-ios-playground")
    }

    private func publicSources() throws -> [String] {
        let directory = repositoryRoot.appendingPathComponent("apple/Sources/iOS/edesign-kit")
        return try FileManager.default.contentsOfDirectory(at: directory, includingPropertiesForKeys: nil)
            .filter { $0.pathExtension == "swift" }
            .map { try String(contentsOf: $0, encoding: .utf8) }
    }

    private var repositoryRoot: URL {
        URL(fileURLWithPath: #filePath).deletingLastPathComponent()
            .deletingLastPathComponent().deletingLastPathComponent().deletingLastPathComponent()
    }
}
