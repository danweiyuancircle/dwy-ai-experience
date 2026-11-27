#if os(iOS)
import SwiftUI
import DesignKitIOS

/// 设置行不附加导航或点击手势，由尾部控件处理输入。
struct SettingsRowExample: View {
    @State private var enabled = true

    var body: some View {
        ESettingsRow(detail: Text("Changes remain local to this demonstration")) {
            Text("Preference")
        } content: {
            ESwitch(isOn: $enabled) { Text("Enabled") }
        }
    }
}
#endif
