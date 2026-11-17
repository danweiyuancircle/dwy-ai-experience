#if os(macOS)
import SwiftUI
import DesignKitMac

struct ManagementListStyleExample: View {
    var body: some View {
        List { ESettingsRow("Application") { ESwitch("Enabled", isOn: .constant(true)) } }
            .modifier(EManagementListStyle()).frame(height: 140)
    }
}
#endif
