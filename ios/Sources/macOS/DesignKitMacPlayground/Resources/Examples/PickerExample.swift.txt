#if os(macOS)
import SwiftUI
import DesignKitMac

/// 独立可复制示例；默认使用应用 bundle，Playground 显式注入其资源 bundle。
struct PickerExample: View {
    private let bundle: Bundle
    private let isEmpty: Bool
    @State private var selected: String? = nil
    @State private var segment = 0
    @State private var includeOption = true

    init(bundle: Bundle = .main, isEmpty: Bool = false) {
        self.bundle = bundle
        self.isEmpty = isEmpty
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            EPicker(resource("Choose an option"), selection: $selected) {
                Text("No selection", bundle: bundle).tag(nil as String?)
                if !isEmpty {
                    Text("First option", bundle: bundle).tag("first" as String?)
                    Text("Disabled option", bundle: bundle).tag("disabled" as String?).disabled(true)
                    if includeOption { Text("Dynamic option", bundle: bundle).tag("dynamic" as String?) }
                }
            }.accessibilityIdentifier("playground.designkit.mac.picker.menu")
            ECheckbox(resource("Include dynamic option"), isOn: $includeOption)
            EPicker(resource("Segment"), selection: $segment, presentation: .segmented) {
                Text("First", bundle: bundle).tag(0)
                Text("Second", bundle: bundle).tag(1)
            }.accessibilityIdentifier("playground.designkit.mac.picker.segment")
            Text(verbatim: selected ?? "nil")
            Text("Selected segment: \(segment)", bundle: bundle).accessibilityIdentifier("playground.designkit.mac.picker.result")
        }
    }

    private func resource(_ value: String.LocalizationValue) -> LocalizedStringResource {
        LocalizedStringResource(value, bundle: .atURL(bundle.bundleURL))
    }
}
#endif
