#if os(macOS)
import SwiftUI
import DesignKitMac

/// 独立可复制示例；默认使用应用 bundle，Playground 显式注入其资源 bundle。
struct SearchFieldExample: View {
    private let bundle: Bundle
    @State private var query = "Alpha"

    init(bundle: Bundle = .main) {
        self.bundle = bundle
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            ESearchField(resource("Search"), text: $query, clearTitle: resource("Clear search"))
                .accessibilityIdentifier("playground.designkit.mac.search-field.input")
            Text(verbatim: query).accessibilityIdentifier("playground.designkit.mac.search-field.result")
        }
    }

    private func resource(_ value: String.LocalizationValue) -> LocalizedStringResource {
        LocalizedStringResource(value, bundle: .atURL(bundle.bundleURL))
    }
}
#endif
