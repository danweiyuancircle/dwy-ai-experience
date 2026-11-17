#if os(macOS)
import SwiftUI
import DesignKitMac

/// 独立可复制示例；默认使用应用 bundle，Playground 显式注入其资源 bundle。
struct ButtonExample: View {
    private let bundle: Bundle
    private let isBusy: Bool
    @State private var count = 0

    init(bundle: Bundle = .main, isBusy: Bool = false) {
        self.bundle = bundle
        self.isBusy = isBusy
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            EButton(resource("Primary action"), emphasis: .primary, isBusy: isBusy) { count += 1 }
                .accessibilityIdentifier("playground.designkit.mac.button.primary")
            EButton(resource("Secondary action")) { count += 1 }
            EButton(resource("Plain action"), emphasis: .plain) { count += 1 }
            EButton(resource("Destructive action"), role: .destructive) { count += 1 }
            EButton(resource("Disabled action"), action: {}).disabled(true)
            Text("Action count: \(count)", bundle: bundle).accessibilityIdentifier("playground.designkit.mac.button.result")
        }
    }

    private func resource(_ value: String.LocalizationValue) -> LocalizedStringResource {
        LocalizedStringResource(value, bundle: .atURL(bundle.bundleURL))
    }
}
#endif
