#if os(macOS)
import SwiftUI
import DesignKitMac

/// 独立可复制示例；默认使用应用 bundle，Playground 显式注入其资源 bundle。
struct StatusBadgeExample: View {
    private let bundle: Bundle

    init(bundle: Bundle = .main) {
        self.bundle = bundle
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            EStatusBadge(resource("Information"), tone: .neutral)
            EStatusBadge(resource("Succeeded"), tone: .success)
            EStatusBadge(resource("Warning"), tone: .warning)
            EStatusBadge(resource("Failed"), tone: .failure)
        }
    }

    private func resource(_ value: String.LocalizationValue) -> LocalizedStringResource {
        LocalizedStringResource(value, bundle: .atURL(bundle.bundleURL))
    }
}
#endif
