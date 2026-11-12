#if os(macOS)
import SwiftUI
import DesignKitMac

/// 独立可复制示例；默认使用应用 bundle，Playground 显式注入其资源 bundle。
struct MenuExample: View {
    private let bundle: Bundle
    @State private var count = 0
    @State private var enabled = false

    init(bundle: Bundle = .main) {
        self.bundle = bundle
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            EMenu(resource("More actions")) {
                Button { count += 1 } label: { Text("Run action", bundle: bundle) }
                Button {} label: { Text("Disabled action", bundle: bundle) }.disabled(true)
                Divider()
                Toggle(isOn: $enabled) { Text("Enabled", bundle: bundle) }
                Button(role: .destructive) { count += 1 } label: { Text("Destructive action", bundle: bundle) }
            }.accessibilityIdentifier("playground.designkit.mac.menu.trigger")
            Text("Action count: \(count)", bundle: bundle)
        }
    }

    private func resource(_ value: String.LocalizationValue) -> LocalizedStringResource {
        LocalizedStringResource(value, bundle: .atURL(bundle.bundleURL))
    }
}
#endif
