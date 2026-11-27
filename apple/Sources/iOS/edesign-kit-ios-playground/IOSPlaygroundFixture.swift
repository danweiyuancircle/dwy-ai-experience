#if os(iOS)
import SwiftUI

/// 组件到真实编译 fixture 的穷举映射；新增组件漏写这里会在编译期报 switch 不完整。
struct IOSPlaygroundFixture: View {
    let component: IOSPlaygroundComponent
    var scenario = IOSPlaygroundScenario.normal

    @ViewBuilder var body: some View {
        switch component {
        case .button: ButtonExample(isBusy: scenario == .busy)
        case .iconAction: IconActionExample(isBusy: scenario == .busy)
        case .menu: MenuExample()
        case .actionGroup: ActionGroupExample(isBusy: scenario == .busy)
        case .picker: PickerExample(isEmpty: scenario == .empty)
        case .switchControl: SwitchExample()
        case .textField: TextFieldExample(isInvalid: scenario == .invalid)
        case .secureField: SecureFieldExample(isInvalid: scenario == .invalid)
        case .searchField: SearchFieldExample()
        case .fieldShell: FieldShellExample(isInvalid: scenario == .invalid)
        case .field: FieldExample(isInvalid: scenario == .invalid)
        case .form: FormExample(isBusy: scenario == .busy, isInvalid: scenario == .invalid)
        case .card: CardExample()
        case .settingsRow: SettingsRowExample()
        case .labelValue: LabelValueExample()
        case .statusBadge: StatusBadgeExample()
        case .stateView: StateViewExample()
        case .noticeHost: NoticeHostExample()
        case .toast: ToastExample()
        case .inlineNotice: InlineNoticeExample()
        case .taskProgress: TaskProgressExample()
        case .alert: AlertExample()
        case .confirm: ConfirmExample()
        case .errorAlert: ErrorAlertExample()
        }
    }
}
#endif
