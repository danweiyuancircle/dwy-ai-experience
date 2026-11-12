#if os(macOS)
import SwiftUI
import DesignKitMac

/// 独立可复制示例；默认使用应用 bundle，Playground 显式注入其资源 bundle。
struct SecureFieldExample: View {
    private let bundle: Bundle
    @State private var password = ""
    @State private var submits = 0

    init(bundle: Bundle = .main) {
        self.bundle = bundle
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            ESecureField(resource("Password"), text: $password).textContentType(.newPassword)
                .onSubmit { submits += 1 }.accessibilityIdentifier("playground.designkit.mac.secure-field.input")
            Text("Character count: \(password.count)", bundle: bundle)
            Text("Submit count: \(submits)", bundle: bundle)
        }
    }

    private func resource(_ value: String.LocalizationValue) -> LocalizedStringResource {
        LocalizedStringResource(value, bundle: .atURL(bundle.bundleURL))
    }
}
#endif
