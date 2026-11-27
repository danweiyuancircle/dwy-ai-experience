#if os(iOS)
import SwiftUI
import DesignKitIOS

/// 不 trim、截断或校验；校验失败只通过 isInvalid 表达。
struct TextFieldExample: View {
    let isInvalid: Bool
    @State private var name = ""

    init(isInvalid: Bool = false) { self.isInvalid = isInvalid }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            ETextField(Text("Name"), text: $name, prompt: Text("Enter a name"), isInvalid: isInvalid)
            Text(verbatim: "Character count: \(name.count)")
        }
    }
}
#endif
