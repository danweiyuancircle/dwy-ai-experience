#if os(macOS)
import SwiftUI
import DesignKitMac

/// 独立可复制示例；默认使用应用 bundle，Playground 显式注入其资源 bundle。
struct ContentStateExample: View {
    private let bundle: Bundle
    @State private var phase = 0
    @State private var count = 0

    init(bundle: Bundle = .main) {
        self.bundle = bundle
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            EPicker(resource("Content state"), selection: $phase) {
                Text("Idle", bundle: bundle).tag(0)
                Text("Loading", bundle: bundle).tag(1)
                Text("Empty", bundle: bundle).tag(2)
                Text("Failed", bundle: bundle).tag(3)
                Text("Succeeded", bundle: bundle).tag(4)
            }
            EContentState(currentPhase, title: resource("Explicit content state"), detail: resource("The caller owns the result and retry decision")) {
                EButton(resource("Retry")) { count += 1 }
            }
            Text("Action count: \(count)", bundle: bundle)
        }
    }

    private var currentPhase: EContentPhase {
        switch phase {
        case 0: .idle
        case 1: .loading
        case 2: .empty
        case 3: .failure
        default: .success
        }
    }

    private func resource(_ value: String.LocalizationValue) -> LocalizedStringResource {
        LocalizedStringResource(value, bundle: .atURL(bundle.bundleURL))
    }
}
#endif
