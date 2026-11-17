#if os(macOS)
import SwiftUI
import DesignKitMac

/// 独立可复制示例；默认使用应用 bundle，Playground 显式注入其资源 bundle。
struct SwitchExample: View {
    private let bundle: Bundle
    @State private var enabled = false

    init(bundle: Bundle = .main) {
        self.bundle = bundle
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            ESwitch(resource("Enabled"), isOn: $enabled).accessibilityIdentifier("playground.designkit.mac.switch.control")
            EButton(resource("Change externally")) { enabled.toggle() }
            Text(enabled ? LocalizedStringKey("On") : LocalizedStringKey("Off"), bundle: bundle)
        }
    }

    private func resource(_ value: String.LocalizationValue) -> LocalizedStringResource {
        LocalizedStringResource(value, bundle: .atURL(bundle.bundleURL))
    }
}
#endif
