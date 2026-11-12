#if os(macOS)
import SwiftUI
import DesignKitMac

/// 独立可复制示例；默认使用应用 bundle，Playground 显式注入其资源 bundle。
struct CardExample: View {
    private let bundle: Bundle
    @State private var count = 0

    init(bundle: Bundle = .main) {
        self.bundle = bundle
    }

    var body: some View {
        ECard {
            VStack(alignment: .leading, spacing: 12) {
                Text("Content card", bundle: bundle).font(.headline)
                Text("Cards do not own navigation or glass effects", bundle: bundle)
                EButton(resource("Run action")) { count += 1 }
                Text("Action count: \(count)", bundle: bundle)
            }
        }
    }

    private func resource(_ value: String.LocalizationValue) -> LocalizedStringResource {
        LocalizedStringResource(value, bundle: .atURL(bundle.bundleURL))
    }
}
#endif
