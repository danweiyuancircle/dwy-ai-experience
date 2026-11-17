#if os(macOS)
import SwiftUI
import DesignKitMac

struct SettingsPageExample: View {
    var body: some View {
        ESettingsPage { EPageHeader(title: Text("Settings")); ETextField("Name", text: .constant("Example")) }.frame(height: 220)
    }
}
#endif
