#if os(macOS)
import SwiftUI
import DesignKitMac

/// 独立可复制示例；默认使用应用 bundle，Playground 显式注入其资源 bundle。
struct TextExample: View {
    private let bundle: Bundle

    init(bundle: Bundle = .main) {
        self.bundle = bundle
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            EText(resource("Page title"), role: .pageTitle)
            EText(resource("Section title"), role: .sectionTitle)
            EText(resource("Body text"), role: .body)
            EText(resource("Secondary text"), role: .secondary)
            EText(resource("Caption text"), role: .caption)
            EText(verbatim: "/Users/example/file.txt", role: .monospaced)
            EText(resource("Failed"), role: .caption, tone: .failure)
            Label("Label with role", systemImage: "tag").eText(.secondary)
        }
    }

    private func resource(_ value: String.LocalizationValue) -> LocalizedStringResource {
        LocalizedStringResource(value, bundle: .atURL(bundle.bundleURL))
    }
}
#endif
