#if os(macOS)
import SwiftUI
import DesignKitMac

/// 独立可复制示例；默认使用应用 bundle，Playground 显式注入其资源 bundle。
struct ComboBoxExample: View {
    private let bundle: Bundle
    private let isEmpty: Bool
    @State private var value = ""
    @State private var suggestions = ["Alpha", "Bravo", "中文输入", "Alpha"]
    @State private var submits = 0
    @State private var editingEnds = 0

    init(bundle: Bundle = .main, isEmpty: Bool = false) {
        self.bundle = bundle
        self.isEmpty = isEmpty
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            EComboBox(resource("Suggestions"), text: $value, suggestions: isEmpty ? [] : suggestions,
                      onEditingEnded: { _ in editingEnds += 1 }) { _ in submits += 1 }
                .accessibilityIdentifier("playground.designkit.mac.combo-box.input")
            EActionGroup {
                EButton(resource("Reverse options")) { suggestions.reverse() }
                EButton(resource("Remove options")) { suggestions = [] }
                EButton(resource("Restore options")) { suggestions = ["Alpha", "Bravo", "中文输入", "Alpha"] }
            }
            Text(verbatim: value).accessibilityIdentifier("playground.designkit.mac.combo-box.result")
            Text("Submit count: \(submits)", bundle: bundle)
            Text("Editing ended: \(editingEnds)", bundle: bundle)
        }
    }

    private func resource(_ value: String.LocalizationValue) -> LocalizedStringResource {
        LocalizedStringResource(value, bundle: .atURL(bundle.bundleURL))
    }
}
#endif
