#if os(macOS)
import SwiftUI
import DesignKitMac

/// 独立可复制示例；默认使用应用 bundle，Playground 显式注入其资源 bundle。
struct TextFieldExample: View {
    private let bundle: Bundle
    @State private var value = "  original text  "
    @State private var submits = 0

    init(bundle: Bundle = .main) {
        self.bundle = bundle
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            ETextField(resource("Name"), text: $value)
                .onSubmit { submits += 1 }.accessibilityIdentifier("playground.designkit.mac.text-field.input")
            Text(verbatim: value).textSelection(.enabled).accessibilityIdentifier("playground.designkit.mac.text-field.result")
            Text("Submit count: \(submits)", bundle: bundle)
        }
    }

    private func resource(_ value: String.LocalizationValue) -> LocalizedStringResource {
        LocalizedStringResource(value, bundle: .atURL(bundle.bundleURL))
    }
}
#endif
