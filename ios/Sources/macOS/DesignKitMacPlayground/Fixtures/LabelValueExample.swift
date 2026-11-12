#if os(macOS)
import SwiftUI
import DesignKitMac

/// 独立可复制示例；默认使用应用 bundle，Playground 显式注入其资源 bundle。
struct LabelValueExample: View {
    private let bundle: Bundle
    @State private var value = "  example.original  "

    init(bundle: Bundle = .main) {
        self.bundle = bundle
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            ETextField(resource("Original text"), text: $value)
            ELabelValue(resource("Value"), value: Text(verbatim: value))
                .accessibilityIdentifier("playground.designkit.mac.label-value.result")
        }
    }

    private func resource(_ value: String.LocalizationValue) -> LocalizedStringResource {
        LocalizedStringResource(value, bundle: .atURL(bundle.bundleURL))
    }
}
#endif
