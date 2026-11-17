#if os(macOS)
import SwiftUI
import DesignKitMac

/// 独立可复制示例；默认使用应用 bundle，Playground 显式注入其资源 bundle。
struct FieldExample: View {
    private let bundle: Bundle
    private let isInvalid: Bool
    @State private var value = ""

    init(bundle: Bundle = .main, isInvalid: Bool = false) {
        self.bundle = bundle
        self.isInvalid = isInvalid
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            EField(resource("Name"), hint: resource("Whitespace and marked text are preserved"),
                   error: isInvalid ? resource("Review this long validation message and correct the value without losing your input") : nil) {
                ETextField(resource("Name"), text: $value).accessibilityIdentifier("playground.designkit.mac.field.input")
            }
            Text(verbatim: value)
        }
    }

    private func resource(_ value: String.LocalizationValue) -> LocalizedStringResource {
        LocalizedStringResource(value, bundle: .atURL(bundle.bundleURL))
    }
}
#endif
