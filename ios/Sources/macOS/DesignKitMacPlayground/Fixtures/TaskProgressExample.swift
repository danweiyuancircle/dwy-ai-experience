#if os(macOS)
import SwiftUI
import DesignKitMac

/// 独立可复制示例；默认使用应用 bundle，Playground 显式注入其资源 bundle。
struct TaskProgressExample: View {
    private let bundle: Bundle
    @State private var fraction = 0.4
    @State private var cancelRequested = false
    @State private var cancelled = false

    init(bundle: Bundle = .main) {
        self.bundle = bundle
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            if cancelled {
                EStatusBadge(resource("Cancelled"), tone: .neutral)
            } else if let progress = EProgressFraction(fraction) {
                ETaskProgress(resource("Transferring"), fraction: progress) {
                    EButton(resource("Cancel task")) { cancelRequested = true }.disabled(cancelRequested)
                }
            } else {
                ENotice(resource("Invalid progress"), tone: .failure)
            }
            Slider(value: $fraction, in: 0...1)
            if cancelRequested { Text("Cancellation requested; waiting for confirmation", bundle: bundle) }
            EButton(resource("Confirm cancellation")) { cancelled = true }
            ETaskProgress(resource("Preparing"))
        }
    }

    private func resource(_ value: String.LocalizationValue) -> LocalizedStringResource {
        LocalizedStringResource(value, bundle: .atURL(bundle.bundleURL))
    }
}
#endif
