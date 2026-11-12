#if os(macOS)
import SwiftUI
import DesignKitMac

/// 独立可复制示例；默认使用应用 bundle，Playground 显式注入其资源 bundle。
struct MenuExample: View {
    private let bundle: Bundle
    @State private var count = 0
    @State private var enabled = false

    init(bundle: Bundle = .main) {
        self.bundle = bundle
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            EMenu(resource("Text-only menu")) {
                Button { count += 1 } label: { Text("Run action", bundle: bundle) }
                Button {} label: { Text("Disabled action", bundle: bundle) }.disabled(true)
            }.accessibilityIdentifier("playground.designkit.mac.menu.text-only")
            EMenu(resource("Icon menu")) {
                Button { count += 1 } label: {
                    Label { Text("Run action", bundle: bundle) } icon: { Image(systemName: "play.fill") }
                }
                Button {} label: {
                    Label { Text("Disabled action", bundle: bundle) } icon: { Image(systemName: "eye.slash") }
                }.disabled(true)
                Button(role: .destructive) { count += 1 } label: {
                    Label { Text("Destructive action", bundle: bundle) } icon: { Image(systemName: "trash") }
                }
            }.accessibilityIdentifier("playground.designkit.mac.menu.with-icons")
            EMenu {
                Section {
                    Button { count += 1 } label: { Text("Run action", bundle: bundle) }
                    Button { count += 1 } label: {
                        Label { Text("Save", bundle: bundle) } icon: { Image(systemName: "square.and.arrow.down") }
                    }
                    Button {} label: { Text("Disabled action", bundle: bundle) }.disabled(true)
                } header: { Text("Actions", bundle: bundle) }
                Toggle(isOn: $enabled) {
                    Label { Text("Enabled", bundle: bundle) } icon: { Image(systemName: "bell") }
                }
                Menu {
                    Button { count += 1 } label: {
                        Label { Text("Retry", bundle: bundle) } icon: { Image(systemName: "arrow.clockwise") }
                    }
                    Button { count += 1 } label: { Text("Cancel", bundle: bundle) }
                } label: {
                    Label { Text("More actions", bundle: bundle) } icon: { Image(systemName: "folder") }
                }
                Divider()
                Button(role: .destructive) { count += 1 } label: { Text("Destructive action", bundle: bundle) }
            } label: {
                Label { Text("Mixed menu", bundle: bundle) } icon: { Image(systemName: "ellipsis.circle") }
            }.accessibilityIdentifier("playground.designkit.mac.menu.trigger")
            Text("Action count: \(count)", bundle: bundle).accessibilityIdentifier("playground.designkit.mac.menu.result")
            Text(enabled ? LocalizedStringKey("On") : LocalizedStringKey("Off"), bundle: bundle)
        }
    }

    private func resource(_ value: String.LocalizationValue) -> LocalizedStringResource {
        LocalizedStringResource(value, bundle: .atURL(bundle.bundleURL))
    }
}
#endif
