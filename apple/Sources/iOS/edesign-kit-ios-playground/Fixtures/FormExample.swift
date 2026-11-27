#if os(iOS)
import SwiftUI
import DesignKitIOS

/// EForm 自带滚动，嵌入其他滚动容器时需要给固定高度。
struct FormExample: View {
    let isBusy: Bool
    let isInvalid: Bool
    @State private var name = ""
    @State private var saved = 0

    init(isBusy: Bool = false, isInvalid: Bool = false) {
        self.isBusy = isBusy
        self.isInvalid = isInvalid
    }

    var body: some View {
        EForm {
            EField(error: isInvalid ? Text("Name is required") : nil) {
                Text("Name")
            } content: {
                ETextField(Text("Name"), text: $name, isInvalid: isInvalid)
            }
            EActionGroup {
                EButton("Save", emphasis: .primary, isBusy: isBusy) { saved += 1 }
                EButton("Cancel") {}
            }
            Text(verbatim: "Save count: \(saved)")
        }
        .frame(height: 320)
    }
}
#endif
