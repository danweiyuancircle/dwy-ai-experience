#if os(macOS)
import SwiftUI
import DesignKitMac

struct SheetCloseButtonExample: View {
    var bundle: Bundle = .main
    @State private var showsSheet = false

    var body: some View {
        Button { showsSheet = true } label: { Text("Show sheet", bundle: bundle) }
            .sheet(isPresented: $showsSheet) {
                ESheetCloseButton(Text("Close", bundle: bundle)) { showsSheet = false }
                    .padding()
            }
    }
}
#endif
