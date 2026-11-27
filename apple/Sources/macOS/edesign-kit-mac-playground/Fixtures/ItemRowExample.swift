#if os(macOS)
import SwiftUI
import DesignKitMac

struct ItemRowExample: View {
    var body: some View {
        EItemRow { Label("Action", systemImage: "doc"); Spacer(); ESwitch("Enabled", isOn: .constant(true)) }
    }
}
#endif
