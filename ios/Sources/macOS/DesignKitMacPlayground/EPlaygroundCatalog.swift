#if os(macOS)
import Foundation

/// 稳定组件身份，不随标题、语言或目录位置变化。辅助值类型随所属组件说明。
public enum EPlaygroundComponent: String, CaseIterable, Identifiable, Sendable {
    case button = "button"
    case iconAction = "icon-action"
    case menu = "menu"
    case actionGroup = "action-group"
    case picker = "picker"
    case switchControl = "switch"
    case checkbox = "checkbox"
    case textField = "text-field"
    case secureField = "secure-field"
    case searchField = "search-field"
    case comboBox = "combo-box"
    case field = "field"
    case fieldShell = "field-shell"
    case card = "card"
    case settingsRow = "settings-row"
    case labelValue = "label-value"
    case statusBadge = "status-badge"
    case contentState = "content-state"
    case notice = "notice"
    case toast = "toast"
    case taskProgress = "task-progress"
    case form = "form"

    public var id: String { "designkit.mac." + rawValue }
    public var module: String { "DesignKitMac" }
    public var minimumOS: String { "macOS 26.0" }

    public var symbol: String {
        switch self {
        case .button: "EButton"
        case .iconAction: "EIconAction"
        case .menu: "EMenu"
        case .actionGroup: "EActionGroup"
        case .picker: "EPicker"
        case .switchControl: "ESwitch"
        case .checkbox: "ECheckbox"
        case .textField: "ETextField"
        case .secureField: "ESecureField"
        case .searchField: "ESearchField"
        case .comboBox: "EComboBox"
        case .field: "EField"
        case .fieldShell: "EFieldShell"
        case .card: "ECard"
        case .settingsRow: "ESettingsRow"
        case .labelValue: "ELabelValue"
        case .statusBadge: "EStatusBadge"
        case .contentState: "EContentState"
        case .notice: "ENotice"
        case .toast: "EToast"
        case .taskProgress: "ETaskProgress"
        case .form: "EForm"
        }
    }

    var fixtureName: String {
        switch self {
        case .button: "ButtonExample"
        case .iconAction: "IconActionExample"
        case .menu: "MenuExample"
        case .actionGroup: "ActionGroupExample"
        case .picker: "PickerExample"
        case .switchControl: "SwitchExample"
        case .checkbox: "CheckboxExample"
        case .textField: "TextFieldExample"
        case .secureField: "SecureFieldExample"
        case .searchField: "SearchFieldExample"
        case .comboBox: "ComboBoxExample"
        case .field: "FieldExample"
        case .fieldShell: "FieldShellExample"
        case .card: "CardExample"
        case .settingsRow: "SettingsRowExample"
        case .labelValue: "LabelValueExample"
        case .statusBadge: "StatusBadgeExample"
        case .contentState: "ContentStateExample"
        case .notice: "NoticeExample"
        case .toast: "ToastExample"
        case .taskProgress: "TaskProgressExample"
        case .form: "FormExample"
        }
    }

    var category: EPlaygroundCategory {
        switch self {
        case .button, .iconAction, .menu, .actionGroup: .actions
        case .picker, .switchControl, .checkbox: .selection
        case .textField, .secureField, .searchField, .comboBox, .field, .fieldShell: .input
        case .card, .settingsRow, .labelValue: .content
        case .statusBadge, .contentState, .notice, .toast, .taskProgress: .feedback
        case .form: .forms
        }
    }

    func matches(_ query: String) -> Bool {
        query.isEmpty || symbol.localizedStandardContains(query) || id.localizedStandardContains(query)
    }
}

enum EPlaygroundCategory: String, CaseIterable, Identifiable {
    case actions = "Actions"
    case selection = "Selection"
    case input = "Input"
    case content = "Content"
    case feedback = "Feedback"
    case forms = "Forms"
    var id: String { rawValue }
}

/// 包资源与展示/复制共用，缺失时抛错，不静默跳到其他组件。
public enum EPlaygroundCatalog {
    public static let version = "0.8.0-beta.4"

    public struct Documentation: Sendable {
        public let markdown: String
        public let swift: String
        public let summary: String
    }

    public enum ResourceError: Error, LocalizedError {
        case missing(String)
        case invalidDocumentation(String)
        public var errorDescription: String? {
            switch self {
            case .missing(let path): "Missing Playground resource: \(path)"
            case .invalidDocumentation(let id): "Missing Playground purpose: \(id)"
            }
        }
    }

    /// 简体中文和英语分别有资源；其他语言使用英语说明，示例 locale 仍保持真实值。
    public static func documentation(for component: EPlaygroundComponent, locale: Locale) throws -> Documentation {
        let language = locale.language.languageCode?.identifier == "zh" ? "zh-Hans" : "en"
        let markdown = try resource(component.rawValue, extension: "md", directory: "Documentation/\(language)")
        let lines = markdown.components(separatedBy: .newlines)
        guard let heading = lines.firstIndex(where: { $0 == "## Purpose" || $0 == "## 用途" }),
              let summary = lines.dropFirst(heading + 1).first(where: { !$0.isEmpty && !$0.hasPrefix("#") }) else {
            throw ResourceError.invalidDocumentation(component.id)
        }
        return try Documentation(markdown: markdown,
                                 swift: resource(component.fixtureName + ".swift", extension: "txt", directory: "Examples"),
                                 summary: summary)
    }

    private static func resource(_ name: String, extension suffix: String, directory: String) throws -> String {
        guard let url = Bundle.module.url(forResource: name, withExtension: suffix, subdirectory: directory) else {
            throw ResourceError.missing(directory + "/" + name + "." + suffix)
        }
        return try String(contentsOf: url, encoding: .utf8)
    }
}
#endif
