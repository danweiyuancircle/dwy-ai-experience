#if os(macOS)
import SwiftUI
import DesignKitMac

/// 原生复杂编辑器复用外壳，输入行为和焦点仍由编辑器拥有。
struct FieldShellExample: View {
    private let bundle: Bundle
    @State private var value = ""
    @FocusState private var focused: Bool

    init(bundle: Bundle = .main) { self.bundle = bundle }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            EFieldShell {
                TextField(text: $value) { Text("Name", bundle: bundle) }
                    .textFieldStyle(.plain)
                    .focused($focused)
                    .accessibilityIdentifier("playground.designkit.mac.field-shell.input")
            }
            EButton(LocalizedStringResource("Focus input", bundle: .atURL(bundle.bundleURL))) { focused = true }
            Text(verbatim: value)
        }
    }
}
#endif
