#if os(macOS)
import SwiftUI
import DesignKitMac

struct PageHeaderExample: View {
    var body: some View {
        EPageHeader(title: Text("Settings"), subtitle: Text("Shared page heading"))
    }
}
#endif
