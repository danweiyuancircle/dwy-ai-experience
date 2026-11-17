#if os(macOS)
import SwiftUI
import DesignKitMac

struct SidebarItemExample: View {
    var body: some View {
        ESidebarItem { Label("Files", systemImage: "folder") }
    }
}
#endif
