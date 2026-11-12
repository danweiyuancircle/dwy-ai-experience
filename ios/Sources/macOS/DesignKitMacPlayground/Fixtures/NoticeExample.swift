#if os(macOS)
import SwiftUI
import DesignKitMac

/// 独立可复制示例；默认使用应用 bundle，Playground 显式注入其资源 bundle。
struct NoticeExample: View {
    private let bundle: Bundle
    @State private var count = 0

    init(bundle: Bundle = .main) {
        self.bundle = bundle
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            ENotice(resource("This important error remains until the caller replaces it"), tone: .failure) {
                EButton(resource("Review details")) { count += 1 }
            }
            Text("Action count: \(count)", bundle: bundle)
        }
    }

    private func resource(_ value: String.LocalizationValue) -> LocalizedStringResource {
        LocalizedStringResource(value, bundle: .atURL(bundle.bundleURL))
    }
}
#endif
