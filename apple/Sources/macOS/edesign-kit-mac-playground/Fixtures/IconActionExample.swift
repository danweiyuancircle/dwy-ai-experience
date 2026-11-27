#if os(macOS)
import SwiftUI
import DesignKitMac

/// 独立可复制示例；默认使用应用 bundle，Playground 显式注入其资源 bundle。
struct IconActionExample: View {
    private let bundle: Bundle
    private let isBusy: Bool
    @State private var count = 0

    init(bundle: Bundle = .main, isBusy: Bool = false) {
        self.bundle = bundle
        self.isBusy = isBusy
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            EIconAction(resource("Add item"), systemImage: "plus", isBusy: isBusy) { count += 1 }
                .accessibilityIdentifier("playground.designkit.mac.icon-action.trigger")
            EIconAction(resource("Custom icon"), action: { count += 1 }) { Image(systemName: "star") }
            Text("Action count: \(count)", bundle: bundle)
        }
    }

    private func resource(_ value: String.LocalizationValue) -> LocalizedStringResource {
        LocalizedStringResource(value, bundle: .atURL(bundle.bundleURL))
    }
}
#endif
