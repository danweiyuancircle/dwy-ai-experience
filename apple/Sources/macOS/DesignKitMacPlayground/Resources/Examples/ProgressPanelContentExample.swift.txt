#if os(macOS)
import SwiftUI
import DesignKitMac

struct ProgressPanelContentExample: View {
    var body: some View {
        EProgressPanelContent(title: Text("Processing"), hint: Text("Cancellation is handled by the host.")) { EButton("Cancel", action: {}) }
    }
}
#endif
