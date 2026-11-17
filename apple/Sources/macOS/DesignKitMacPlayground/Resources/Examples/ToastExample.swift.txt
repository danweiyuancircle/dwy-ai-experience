#if os(macOS)
import SwiftUI
import DesignKitMac

/// 独立可复制示例；默认使用应用 bundle，Playground 显式注入其资源 bundle。
struct ToastExample: View {
    private let bundle: Bundle
    @State private var message: EToastMessage?
    @State private var count = 0

    init(bundle: Bundle = .main) {
        self.bundle = bundle
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            EActionGroup {
                EButton(resource("Show success")) { count += 1; message = EToastMessage(resource("Action completed")) }
                EButton(resource("Replace message")) { count += 1; message = EToastMessage(resource("Saved")) }
                EButton(resource("Clear message")) { message = nil }
            }
            EToast(message: $message, dismissTitle: resource("Dismiss notice"))
            Text("Action count: \(count)", bundle: bundle)
        }
    }

    private func resource(_ value: String.LocalizationValue) -> LocalizedStringResource {
        LocalizedStringResource(value, bundle: .atURL(bundle.bundleURL))
    }
}
#endif
