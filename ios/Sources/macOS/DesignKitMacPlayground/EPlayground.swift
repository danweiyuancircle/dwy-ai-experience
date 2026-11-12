#if os(macOS)
import SwiftUI
import AppKit
import DesignKitMac

/// 可嵌入的 Mac 组件目录。宿主拥有窗口和项目组合；本视图不修改主题中心或用户偏好。
/// 项目内容不应再包含整页 ScrollView，详情区已提供滚动承载与局部环境。
public struct EPlayground<ProjectContent: View>: View {
    @State private var selection: EPlaygroundSelection? = .component(.button)
    @State private var query = ""
    @State private var previewOptions = EPreviewOptions()
    @State private var showPreviewSettings = false
    private let projectTitle: Text?
    private let projectContent: ProjectContent

    public init(projectTitle: Text, @ViewBuilder projectContent: () -> ProjectContent) {
        self.projectTitle = projectTitle
        self.projectContent = projectContent()
    }

    public var body: some View {
        VStack(spacing: 0) {
            HStack {
                Spacer()
                Button { showPreviewSettings.toggle() } label: {
                    Label { Text("Preview settings", bundle: .module) } icon: {
                        Image(systemName: "slider.horizontal.3")
                    }
                }
                .accessibilityIdentifier("playground.preview.settings")
                .popover(isPresented: $showPreviewSettings, arrowEdge: .bottom) {
                    EPreviewControls(options: $previewOptions).padding(16).frame(width: 340)
                }
            }
            .padding(.horizontal, 16).padding(.vertical, 8)
            Divider()
            HSplitView {
                VStack(spacing: 0) {
                    ESearchField(resource("Search components"), text: $query, clearTitle: resource("Clear search"))
                        .accessibilityIdentifier("playground.catalog.search")
                        .padding(12)
                    List(selection: $selection) {
                        ForEach(EPlaygroundCategory.allCases) { category in
                            let components = components(in: category)
                            if !components.isEmpty {
                                Section {
                                    ForEach(components) { component in
                                        Text(verbatim: component.symbol)
                                            .tag(EPlaygroundSelection.component(component))
                                            .accessibilityIdentifier("playground.\(component.id).row")
                                    }
                                } header: {
                                    Text(LocalizedStringKey(category.rawValue), bundle: .module)
                                }
                            }
                        }
                        if let projectTitle {
                            Section {
                                projectTitle.tag(EPlaygroundSelection.project)
                                    .accessibilityIdentifier("playground.project.row")
                            } header: { Text("Project compositions", bundle: .module) }
                        }
                    }
                    Text("DesignKitMac · \(EPlaygroundCatalog.version)", bundle: .module)
                        .font(.caption).foregroundStyle(.secondary).padding(12)
                    if let version = Bundle.main.object(forInfoDictionaryKey: "CFBundleShortVersionString") as? String,
                       let build = Bundle.main.object(forInfoDictionaryKey: "CFBundleVersion") as? String {
                        Text("Host: \(version) (\(build))", bundle: .module).font(.caption).padding(.bottom, 8)
                    } else {
                        Text("Host build metadata is unavailable", bundle: .module).font(.caption).padding(.bottom, 8)
                    }
                }
                .frame(minWidth: 190, idealWidth: 220, maxWidth: 300)
                Group {
                    switch selection {
                    case .component(let component):
                        EPlaygroundDetail(component: component, options: previewOptions).id(component)
                    case .project:
                        EPlaygroundProjectDetail(title: projectTitle, content: projectContent, options: previewOptions)
                    case nil:
                        Text("Select a component", bundle: .module).frame(maxWidth: .infinity, maxHeight: .infinity)
                    }
                }
                .frame(minWidth: 420, maxWidth: .infinity, maxHeight: .infinity)
            }
        }
        .frame(minWidth: 640, minHeight: 500)
    }

    private func components(in category: EPlaygroundCategory) -> [EPlaygroundComponent] {
        EPlaygroundComponent.allCases.filter { $0.category == category && $0.matches(query) }
    }

    private func resource(_ key: String.LocalizationValue) -> LocalizedStringResource {
        LocalizedStringResource(key, bundle: .atURL(Bundle.module.bundleURL))
    }
}

public extension EPlayground where ProjectContent == EmptyView {
    /// 仅展示基础组件；不会创建空的项目业务模块。
    init() {
        projectTitle = nil
        projectContent = EmptyView()
    }
}

private enum EPlaygroundSelection: Hashable {
    case component(EPlaygroundComponent)
    case project
}

private struct EPlaygroundDetail: View {
    @Environment(\.locale) private var locale
    let component: EPlaygroundComponent
    let options: EPreviewOptions
    @State private var resetID = 0
    @State private var scenario = EPlaygroundScenario.normal
    @State private var copyResult: LocalizedStringResource?
    @State private var showDocumentation = false
    @State private var showSwift = false

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                Text(verbatim: component.symbol).font(.title2).accessibilityAddTraits(.isHeader)
                Text(verbatim: "\(component.id) · \(component.module) · \(component.minimumOS)")
                    .font(.caption).foregroundStyle(.secondary)
                EPreviewArea(options: options) {
                    EPlaygroundFixture(component: component, scenario: scenario)
                        .id(resetID)
                        .disabled(scenario == .disabled)
                }
                HStack {
                    EPicker(resource("Example state"), selection: $scenario) {
                        ForEach(component.scenarios) { item in
                            Text(LocalizedStringKey(item.rawValue), bundle: .module).tag(item)
                        }
                    }
                    .frame(maxWidth: 220)
                    .accessibilityIdentifier("playground.\(component.id).state")
                    Spacer()
                    EButton(resource("Reset example")) { resetID += 1 }
                        .accessibilityIdentifier("playground.\(component.id).reset")
                }
                documentation
                if let copyResult { Text(copyResult).font(.caption) }
            }
            .padding(20)
            .frame(maxWidth: .infinity, alignment: .leading)
        }
    }

    @ViewBuilder private var documentation: some View {
        switch Result(catching: {
            try EPlaygroundCatalog.documentation(for: component, locale: options.locale ?? locale)
        }) {
        case .success(let document):
            VStack(alignment: .leading, spacing: 12) {
                Text(verbatim: document.summary).textSelection(.enabled)
                    .foregroundStyle(.secondary)
                EActionGroup {
                    EButton(resource("Copy Swift example")) { copy(document.swift) }
                        .accessibilityIdentifier("playground.\(component.id).copy-swift")
                    EButton(resource("Copy Markdown")) { copy(document.markdown) }
                        .accessibilityIdentifier("playground.\(component.id).copy-markdown")
                }
                DisclosureGroup(isExpanded: $showDocumentation) {
                    Text(verbatim: document.markdown).textSelection(.enabled)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .accessibilityIdentifier("playground.\(component.id).documentation")
                } label: {
                    Text("Usage and constraints", bundle: .module)
                }
                DisclosureGroup(isExpanded: $showSwift) {
                    ScrollView(.horizontal) {
                        Text(verbatim: document.swift).font(.body.monospaced()).textSelection(.enabled)
                            .accessibilityIdentifier("playground.\(component.id).source")
                    }
                } label: {
                    Text("Swift example", bundle: .module)
                }
            }
        case .failure(let error):
            ENotice(Text(verbatim: error.localizedDescription), tone: .failure) { EmptyView() }
        }
    }

    private func copy(_ text: String) {
        NSPasteboard.general.clearContents()
        copyResult = NSPasteboard.general.setString(text, forType: .string)
            ? resource("Copied") : resource("Could not write to the clipboard")
    }

    private func resource(_ key: String.LocalizationValue) -> LocalizedStringResource {
        LocalizedStringResource(key, bundle: .atURL(Bundle.module.bundleURL))
    }
}

private struct EPlaygroundProjectDetail<Content: View>: View {
    let title: Text?
    let content: Content
    let options: EPreviewOptions
    @State private var resetID = 0

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                if let title { title.font(.title2).accessibilityAddTraits(.isHeader) }
                Text("Project examples are supplied and documented by the host", bundle: .module)
                    .foregroundStyle(.secondary)
                EPreviewArea(options: options) { content.id(resetID) }
                EButton(LocalizedStringResource("Reset example", bundle: .atURL(Bundle.module.bundleURL))) { resetID += 1 }
                    .accessibilityIdentifier("playground.project.reset")
            }
            .padding(20)
        }
    }
}

enum EPlaygroundScenario: String, CaseIterable, Identifiable {
    case normal = "Normal"
    case disabled = "Disabled"
    case busy = "Busy"
    case invalid = "Invalid"
    case empty = "Empty"
    var id: String { rawValue }
}

extension EPlaygroundComponent {
    var scenarios: [EPlaygroundScenario] {
        switch self {
        case .button, .iconAction, .actionGroup: [.normal, .disabled, .busy]
        case .field: [.normal, .disabled, .invalid]
        case .form: [.normal, .disabled, .busy, .invalid]
        case .picker, .comboBox: [.normal, .disabled, .empty]
        default: [.normal, .disabled]
        }
    }
}

struct EPlaygroundFixture: View {
    let component: EPlaygroundComponent
    var scenario = EPlaygroundScenario.normal

    @ViewBuilder var body: some View {
        switch component {
        case .button: ButtonExample(bundle: .module, isBusy: scenario == .busy)
        case .iconAction: IconActionExample(bundle: .module, isBusy: scenario == .busy)
        case .menu: MenuExample(bundle: .module)
        case .actionGroup: ActionGroupExample(bundle: .module, isBusy: scenario == .busy)
        case .picker: PickerExample(bundle: .module, isEmpty: scenario == .empty)
        case .switchControl: SwitchExample(bundle: .module)
        case .checkbox: CheckboxExample(bundle: .module)
        case .textField: TextFieldExample(bundle: .module)
        case .secureField: SecureFieldExample(bundle: .module)
        case .searchField: SearchFieldExample(bundle: .module)
        case .comboBox: ComboBoxExample(bundle: .module, isEmpty: scenario == .empty)
        case .field: FieldExample(bundle: .module, isInvalid: scenario == .invalid)
        case .fieldShell: FieldShellExample(bundle: .module)
        case .card: CardExample(bundle: .module)
        case .settingsRow: SettingsRowExample(bundle: .module)
        case .labelValue: LabelValueExample(bundle: .module)
        case .statusBadge: StatusBadgeExample(bundle: .module)
        case .contentState: ContentStateExample(bundle: .module)
        case .notice: NoticeExample(bundle: .module)
        case .toast: ToastExample(bundle: .module)
        case .taskProgress: TaskProgressExample(bundle: .module)
        case .form: FormExample(bundle: .module, isBusy: scenario == .busy, isInvalid: scenario == .invalid)
        }
    }
}
#endif
