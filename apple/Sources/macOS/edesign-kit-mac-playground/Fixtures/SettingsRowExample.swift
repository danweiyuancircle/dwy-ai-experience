#if os(macOS)
import SwiftUI
import DesignKitMac

/// 独立可复制示例；默认使用应用 bundle，Playground 显式注入其资源 bundle。
struct SettingsRowExample: View {
    private let bundle: Bundle
    @State private var enabled = false

    init(bundle: Bundle = .main) {
        self.bundle = bundle
    }

    var body: some View {
        ESettingsRow(resource("Background work"), detail: resource("This long explanation wraps and the control moves below the title when space is limited")) {
            ESwitch(resource("Enabled"), isOn: $enabled).labelsHidden()
                .accessibilityIdentifier("playground.designkit.mac.settings-row.control")
        }
    }

    private func resource(_ value: String.LocalizationValue) -> LocalizedStringResource {
        LocalizedStringResource(value, bundle: .atURL(bundle.bundleURL))
    }
}
#endif
