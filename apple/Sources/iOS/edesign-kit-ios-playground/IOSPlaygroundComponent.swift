import Foundation

/// 双语文案。Playground 是开发工具，文案随代码内联以便在没有 iOS SDK 的环境下也能测试完整性，不依赖 .strings 资源。
public struct IOSPlaygroundText: Sendable, Hashable {
    public let en: String
    public let zh: String

    public init(en: String, zh: String) {
        self.en = en
        self.zh = zh
    }

    /// 仅中文 locale 返回中文，其他语言回退英文。
    public func resolve(_ locale: Locale) -> String {
        locale.language.languageCode?.identifier == "zh" ? zh : en
    }
}

/// 稳定的组件身份，不随标题、语言或目录位置变化。新增公开 E* 可视组件时必须在此补项，目录覆盖测试会拦截遗漏。
public enum IOSPlaygroundComponent: String, CaseIterable, Identifiable, Sendable {
    case button = "button"
    case iconAction = "icon-action"
    case menu = "menu"
    case actionGroup = "action-group"
    case picker = "picker"
    case switchControl = "switch"
    case textField = "text-field"
    case secureField = "secure-field"
    case searchField = "search-field"
    case fieldShell = "field-shell"
    case field = "field"
    case form = "form"
    case card = "card"
    case settingsRow = "settings-row"
    case labelValue = "label-value"
    case statusBadge = "status-badge"
    case stateView = "state-view"
    case noticeHost = "notice-host"
    case toast = "toast"
    case inlineNotice = "inline-notice"
    case taskProgress = "task-progress"
    case alert = "alert"
    case confirm = "confirm"
    case errorAlert = "error-alert"

    public var id: String { "designkit.ios." + rawValue }
    public var module: String { "DesignKitIOS" }
    public var minimumOS: String { "iOS 18.0" }

    public var symbol: String {
        switch self {
        case .button: "EButton"
        case .iconAction: "EIconAction"
        case .menu: "EMenu"
        case .actionGroup: "EActionGroup"
        case .picker: "EPicker"
        case .switchControl: "ESwitch"
        case .textField: "ETextField"
        case .secureField: "ESecureField"
        case .searchField: "ESearchField"
        case .fieldShell: "EFieldShell"
        case .field: "EField"
        case .form: "EForm"
        case .card: "ECard"
        case .settingsRow: "ESettingsRow"
        case .labelValue: "ELabelValue"
        case .statusBadge: "EStatusBadge"
        case .stateView: "EStateView"
        case .noticeHost: "ENoticeHost"
        case .toast: "EToast"
        case .inlineNotice: "EInlineNotice"
        case .taskProgress: "ETaskProgress"
        case .alert: "EAlert"
        case .confirm: "EConfirm"
        case .errorAlert: "EErrorAlert"
        }
    }

    /// 示例结构体名，与 `Fixtures/` 文件名一致。
    public var fixtureName: String { String(symbol.dropFirst()) + "Example" }

    public var category: IOSPlaygroundCategory {
        switch self {
        case .button, .iconAction, .menu, .actionGroup: .actions
        case .picker, .switchControl: .selection
        case .textField, .secureField, .searchField, .fieldShell, .field, .form: .input
        case .card, .settingsRow, .labelValue, .statusBadge, .stateView: .content
        case .noticeHost, .toast, .inlineNotice, .taskProgress: .feedback
        case .alert, .confirm, .errorAlert: .dialogs
        }
    }

    /// 示例在 Playground 中可切换的状态。第一项必须是 normal；实际改变示例内容的状态（busy/invalid/empty）必须有对应 fixture 参数。
    public var scenarios: [IOSPlaygroundScenario] {
        switch self {
        case .button, .iconAction, .actionGroup: [.normal, .disabled, .busy]
        case .textField, .secureField, .fieldShell, .field: [.normal, .disabled, .invalid]
        case .form: [.normal, .disabled, .busy, .invalid]
        case .picker: [.normal, .disabled, .empty]
        default: [.normal, .disabled]
        }
    }

    /// 搜索同时匹配公开符号与稳定 ID；空白查询匹配全部。
    public func matches(_ query: String) -> Bool {
        let term = query.trimmingCharacters(in: .whitespacesAndNewlines)
        return term.isEmpty || symbol.localizedCaseInsensitiveContains(term) || id.localizedCaseInsensitiveContains(term)
    }
}

public enum IOSPlaygroundCategory: String, CaseIterable, Identifiable, Sendable {
    case actions
    case selection
    case input
    case content
    case feedback
    case dialogs

    public var id: String { rawValue }

    public var title: IOSPlaygroundText {
        switch self {
        case .actions: IOSPlaygroundText(en: "Actions", zh: "操作")
        case .selection: IOSPlaygroundText(en: "Selection", zh: "选择")
        case .input: IOSPlaygroundText(en: "Input and forms", zh: "输入与表单")
        case .content: IOSPlaygroundText(en: "Content", zh: "内容")
        case .feedback: IOSPlaygroundText(en: "Feedback", zh: "反馈")
        case .dialogs: IOSPlaygroundText(en: "Dialogs", zh: "弹框")
        }
    }
}

public enum IOSPlaygroundScenario: String, CaseIterable, Identifiable, Sendable {
    case normal
    case disabled
    case busy
    case invalid
    case empty

    public var id: String { rawValue }

    public var title: IOSPlaygroundText {
        switch self {
        case .normal: IOSPlaygroundText(en: "Normal", zh: "正常")
        case .disabled: IOSPlaygroundText(en: "Disabled", zh: "禁用")
        case .busy: IOSPlaygroundText(en: "Busy", zh: "忙磌")
        case .invalid: IOSPlaygroundText(en: "Invalid", zh: "校验失败")
        case .empty: IOSPlaygroundText(en: "No options", zh: "无候选")
        }
    }
}

/// 目录选中项：组件详情或主题/设计令牌页。
public enum IOSPlaygroundDestination: Hashable, Sendable {
    case component(IOSPlaygroundComponent)
    case tokens

    /// 主题页没有符号名，用关键词让搜索 "theme" / "令牌" 也能找到。
    public func matches(_ query: String) -> Bool {
        switch self {
        case .component(let component): component.matches(query)
        case .tokens:
            query.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
                || ["theme", "token", "design", "主题", "令牌", "设计"].contains { keyword in
                    keyword.localizedCaseInsensitiveContains(query.trimmingCharacters(in: .whitespacesAndNewlines))
                }
        }
    }
}

/// 仅局部预览值；不写 ThemeManager、LocalizationManager 或 UserDefaults。
public struct IOSPreviewOptions: Equatable, Sendable {
    public enum Appearance: String, CaseIterable, Identifiable, Sendable {
        case system
        case light
        case dark
        public var id: String { rawValue }

        public var title: IOSPlaygroundText {
            switch self {
            case .system: IOSPlaygroundText(en: "Inherit", zh: "跟随宿主")
            case .light: IOSPlaygroundText(en: "Light", zh: "浅色")
            case .dark: IOSPlaygroundText(en: "Dark", zh: "深色")
            }
        }
    }

    public var appearance = Appearance.system
    public var largeText = false
    public var alternateBrand = false
    public var floatingPlacement = false

    public init() {}

    public var isDefault: Bool { self == IOSPreviewOptions() }

    public mutating func reset() { self = IOSPreviewOptions() }
}

/// 外层界面文案的双语选择；与组件说明使用同一套 locale 规则。
public struct IOSPlaygroundChrome: Sendable {
    public let locale: Locale

    public init(locale: Locale) { self.locale = locale }

    public func callAsFunction(_ en: String, _ zh: String) -> String {
        IOSPlaygroundText(en: en, zh: zh).resolve(locale)
    }
}
