#if os(iOS)
import SwiftUI
import UIKit
import DesignKitIOS

/// 可嵌入的 iOS 组件目录。宿主拥有窗口与 scene；本视图不修改 ThemeManager 或用户偏好。
/// 自带 NavigationSplitView：iPhone 折叠为单栏导航，iPad 横屏双栏。不要再嵌到另一个 NavigationStack 里。
public struct IOSPlayground: View {
    @Environment(\.locale) private var locale
    @State private var selection: IOSPlaygroundDestination?
    @State private var query = ""
    @State private var previewOptions = IOSPreviewOptions()
    @State private var showPreviewSettings = false
    @State private var columnVisibility = NavigationSplitViewVisibility.automatic

    public init() {}

    public var body: some View {
        let text = IOSPlaygroundChrome(locale: locale)
        NavigationSplitView(columnVisibility: $columnVisibility) {
            catalog(text)
                .navigationTitle(Text(verbatim: "DesignKitIOS"))
                .searchable(text: $query, prompt: Text(verbatim: text("Search components", "搜索组件")))
        } detail: {
            detail(text)
        }
        .sheet(isPresented: $showPreviewSettings) {
            IOSPreviewControls(options: $previewOptions)
                .presentationDetents([.medium, .large])
        }
    }

    private func catalog(_ text: IOSPlaygroundChrome) -> some View {
        List(selection: $selection) {
            if IOSPlaygroundDestination.tokens.matches(query) {
                Section {
                    Text(verbatim: text("Theme and design tokens", "主题与设计令牌"))
                        .tag(IOSPlaygroundDestination.tokens)
                        .accessibilityIdentifier("playground.tokens.row")
                }
            }
            ForEach(IOSPlaygroundCategory.allCases) { category in
                let components = IOSPlaygroundComponent.allCases.filter { $0.category == category && $0.matches(query) }
                if !components.isEmpty {
                    Section {
                        ForEach(components) { component in
                            Text(verbatim: component.symbol)
                                .tag(IOSPlaygroundDestination.component(component))
                                .accessibilityIdentifier("playground.\(component.id).row")
                        }
                    } header: {
                        Text(verbatim: category.title.resolve(locale))
                    }
                }
            }
            Section {
                Text(verbatim: "DesignKitIOS \u{00B7} \(IOSPlaygroundCatalog.version)")
                    .font(.caption).foregroundStyle(.secondary)
            }
        }
        .overlay {
            if !query.isEmpty, !IOSPlaygroundDestination.tokens.matches(query),
               !IOSPlaygroundComponent.allCases.contains(where: { $0.matches(query) }) {
                ContentUnavailableView.search(text: query)
            }
        }
    }

    @ViewBuilder private func detail(_ text: IOSPlaygroundChrome) -> some View {
        Group {
            switch selection {
            case .component(let component):
                IOSPlaygroundDetail(component: component, options: previewOptions)
                    .id(component)
            case .tokens:
                IOSPlaygroundTokens(options: previewOptions)
            case nil:
                ContentUnavailableView(text("Select a component", "请选择组件"), systemImage: "square.grid.2x2")
            }
        }
        .toolbar {
            ToolbarItem(placement: .primaryAction) {
                Button { showPreviewSettings = true } label: {
                    Label(text("Preview settings", "预览设置"), systemImage: "slider.horizontal.3")
                }
                .accessibilityIdentifier("playground.preview.settings")
            }
        }
    }
}

private struct IOSPlaygroundDetail: View {
    @Environment(\.locale) private var locale
    let component: IOSPlaygroundComponent
    let options: IOSPreviewOptions
    @State private var resetID = 0
    @State private var scenario = IOSPlaygroundScenario.normal
    @State private var copyResult: String?
    @State private var showSwift = false
    @State private var exampleSource: Result<String, Error>?

    var body: some View {
        let text = IOSPlaygroundChrome(locale: locale)
        let doc = component.documentation
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                Text(verbatim: component.symbol).font(.title2.bold()).accessibilityAddTraits(.isHeader)
                Text(verbatim: "\(component.id) \u{00B7} \(component.module) \u{00B7} \(component.minimumOS)")
                    .font(.caption).foregroundStyle(.secondary)
                IOSPreviewArea(options: options) {
                    IOSPlaygroundFixture(component: component, scenario: scenario)
                        .id(resetID)
                        .disabled(scenario == .disabled)
                }
                .accessibilityIdentifier("playground.\(component.id).preview")
                stateRow(text)
                Text(verbatim: doc.summary.resolve(locale)).foregroundStyle(.secondary)
                bulletSection(text("Supported capabilities", "支持的能力"), items: doc.capabilities,
                              identifier: "playground.\(component.id).capabilities")
                bulletSection(text("Usage and constraints", "用法与约束"), items: doc.constraints,
                              identifier: "playground.\(component.id).constraints")
                swiftSection(text)
                if let copyResult { Text(verbatim: copyResult).font(.caption).accessibilityIdentifier("playground.\(component.id).copy-result") }
            }
            .padding(16)
            .frame(maxWidth: .infinity, alignment: .leading)
        }
        .navigationTitle(Text(verbatim: component.symbol))
        .navigationBarTitleDisplayMode(.inline)
        .task(id: component) { exampleSource = Result { try IOSPlaygroundCatalog.exampleSource(for: component) } }
    }

    private func stateRow(_ text: IOSPlaygroundChrome) -> some View {
        HStack {
            Picker(text("Example state", "示例状态"), selection: $scenario) {
                ForEach(component.scenarios) { item in
                    Text(verbatim: item.title.resolve(locale)).tag(item)
                }
            }
            .pickerStyle(.menu)
            .accessibilityIdentifier("playground.\(component.id).state")
            Spacer()
            Button(text("Reset example", "重置示例")) {
                scenario = .normal
                resetID += 1
            }
            .buttonStyle(.bordered)
            .accessibilityIdentifier("playground.\(component.id).reset")
        }
    }

    private func bulletSection(_ title: String, items: [IOSPlaygroundText], identifier: String) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(verbatim: title).font(.headline).accessibilityAddTraits(.isHeader)
            ForEach(Array(items.enumerated()), id: \.offset) { _, item in
                Label {
                    Text(verbatim: item.resolve(locale))
                } icon: {
                    Image(systemName: "checkmark.circle").foregroundStyle(.secondary).accessibilityHidden(true)
                }
                .labelStyle(.titleAndIcon)
            }
        }
        .accessibilityElement(children: .contain)
        .accessibilityIdentifier(identifier)
    }

    @ViewBuilder private func swiftSection(_ text: IOSPlaygroundChrome) -> some View {
        switch exampleSource {
        case .success(let source):
            Button(text("Copy Swift example", "复制 Swift 示例")) {
                UIPasteboard.general.string = source
                copyResult = text("Copied", "已复制")
            }
            .buttonStyle(.borderedProminent)
            .accessibilityIdentifier("playground.\(component.id).copy-swift")
            DisclosureGroup(isExpanded: $showSwift) {
                ScrollView(.horizontal) {
                    Text(verbatim: source).font(.footnote.monospaced()).textSelection(.enabled)
                        .accessibilityIdentifier("playground.\(component.id).source")
                }
            } label: {
                Text(verbatim: text("Swift example", "Swift 示例"))
            }
        case .failure(let error):
            Label {
                Text(verbatim: error.localizedDescription)
            } icon: {
                Image(systemName: "exclamationmark.triangle")
            }
            .foregroundStyle(.red)
        case nil:
            ProgressView().accessibilityHidden(true)
        }
    }
}

/// 令牌展示直接读取 EControlTheme 的实际值，不自己维护第二份数字表。
private struct IOSPlaygroundTokens: View {
    @Environment(\.locale) private var locale
    let options: IOSPreviewOptions

    var body: some View {
        let text = IOSPlaygroundChrome(locale: locale)
        let theme = options.alternateBrand ? IOSPreviewArea<EmptyView>.alternateTheme : EControlTheme.standard
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                Text(verbatim: text("Theme and design tokens", "主题与设计令牌")).font(.title2.bold())
                    .accessibilityAddTraits(.isHeader)
                Text(verbatim: text("Values come from EControlTheme and follow the preview settings.",
                                    "数值直接来自 EControlTheme，并跟随预览设置。"))
                    .foregroundStyle(.secondary)
                IOSPreviewArea(options: options) {
                    VStack(alignment: .leading, spacing: 20) {
                        group(text("Colors", "颜色"), swatches(theme))
                        group(text("Typography", "字体"), typography(theme))
                        group(text("Spacing", "间距"), numbers(theme.spacing.values))
                        group(text("Size", "尺寸"), numbers(theme.size.values))
                        group(text("Radius", "圆角"), numbers(theme.radius.values))
                    }
                }
                .accessibilityIdentifier("playground.tokens.preview")
            }
            .padding(16)
            .frame(maxWidth: .infinity, alignment: .leading)
        }
        .navigationTitle(Text(verbatim: text("Theme and design tokens", "主题与设计令牌")))
        .navigationBarTitleDisplayMode(.inline)
    }

    private func group(_ title: String, _ content: some View) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(verbatim: title).font(.headline)
            content
        }
    }

    private func swatches(_ theme: EControlTheme) -> some View {
        let entries: [(String, Color)] = [
            ("background", theme.colors.background), ("surface", theme.colors.surface),
            ("elevatedSurface", theme.colors.elevatedSurface), ("separator", theme.colors.separator),
            ("success", theme.colors.success), ("warning", theme.colors.warning), ("danger", theme.colors.danger),
            ("selection", theme.colors.selection),
            ("accent", theme.accent.light), ("accent (dark)", theme.accent.dark),
        ]
        return VStack(alignment: .leading, spacing: 8) {
            ForEach(entries, id: \.0) { name, color in
                HStack(spacing: 12) {
                    RoundedRectangle(cornerRadius: 6).fill(color).frame(width: 44, height: 28)
                        .overlay { RoundedRectangle(cornerRadius: 6).strokeBorder(Color.primary.opacity(0.2)) }
                        .accessibilityHidden(true)
                    Text(verbatim: name).font(.callout.monospaced())
                }
            }
        }
    }

    private func typography(_ theme: EControlTheme) -> some View {
        let entries: [(String, Font)] = [
            ("title", theme.typography.title), ("sectionTitle", theme.typography.sectionTitle),
            ("body", theme.typography.body), ("secondary", theme.typography.secondary),
            ("caption", theme.typography.caption), ("monospaced", theme.typography.monospaced),
        ]
        return VStack(alignment: .leading, spacing: 6) {
            ForEach(entries, id: \.0) { name, font in
                Text(verbatim: name).font(font)
            }
        }
    }

    private func numbers(_ values: [(String, CGFloat)]) -> some View {
        VStack(alignment: .leading, spacing: 4) {
            ForEach(values, id: \.0) { name, value in
                LabeledContent {
                    Text(verbatim: value.formatted())
                } label: {
                    Text(verbatim: name).font(.callout.monospaced())
                }
            }
        }
    }
}

/// 仅用于令牌展示的列表化；公开令牌指标变化时这里需同步，否则新令牌不会出现在页面上。
private extension EControlTheme.Spacing {
    var values: [(String, CGFloat)] {
        [("inline", inline), ("fieldLabel", fieldLabel), ("controlGroup", controlGroup), ("formRow", formRow),
         ("group", group), ("section", section), ("cardInset", cardInset)]
    }
}

private extension EControlTheme.Size {
    var values: [(String, CGFloat)] {
        [("iconGlyph", iconGlyph), ("iconHit", iconHit), ("action", action), ("field", field),
         ("search", search), ("row", row), ("toolbarAction", toolbarAction)]
    }
}

private extension EControlTheme.Radius {
    var values: [(String, CGFloat)] { [("field", field), ("card", card), ("group", group)] }
}
#endif
