#if os(macOS)
import SwiftUI
import DesignKitMac

/// 独立可复制示例；默认使用应用 bundle，Playground 显式注入其资源 bundle。
struct FormExample: View {
    private let bundle: Bundle
    private let isBusy: Bool
    private let isInvalid: Bool
    @State private var value = ""
    @State private var count = 0

    init(bundle: Bundle = .main, isBusy: Bool = false, isInvalid: Bool = false) {
        self.bundle = bundle
        self.isBusy = isBusy
        self.isInvalid = isInvalid
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            EForm {
                EField(resource("Name"), error: isInvalid ? resource("Name is required") : nil) {
                    ETextField(resource("Name"), text: $value)
                }
                Text("Long form content remains scrollable while actions stay reachable", bundle: bundle)
                ETextField(resource("Read only"), text: .constant("Original value")).disabled(true)
            } actions: {
                EActionGroup {
                    EButton(resource("Cancel")) { count += 1 }
                    EButton(resource("Save"), emphasis: .primary, isBusy: isBusy) { count += 1 }
                }
            }.frame(height: 240)
            Text("Action count: \(count)", bundle: bundle)
        }
    }

    private func resource(_ value: String.LocalizationValue) -> LocalizedStringResource {
        LocalizedStringResource(value, bundle: .atURL(bundle.bundleURL))
    }
}
#endif
