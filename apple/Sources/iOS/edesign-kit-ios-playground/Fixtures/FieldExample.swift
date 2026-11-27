#if os(iOS)
import SwiftUI
import DesignKitIOS

/// 错误优先于 hint；内部编辑器仍需自己的可访问标题。
struct FieldExample: View {
    let isInvalid: Bool
    @State private var name = ""

    init(isInvalid: Bool = false) { self.isInvalid = isInvalid }

    var body: some View {
        EField(hint: Text("Whitespace is preserved"), error: isInvalid ? Text("Enter a value before saving") : nil) {
            Text("Name")
        } content: {
            ETextField(Text("Name"), text: $name, isInvalid: isInvalid)
        }
    }
}
#endif
