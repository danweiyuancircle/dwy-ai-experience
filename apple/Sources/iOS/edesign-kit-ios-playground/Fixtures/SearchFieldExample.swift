#if os(iOS)
import SwiftUI
import DesignKitIOS

/// 清空按钮仅在有文本时出现，不隐式发起请求。
struct SearchFieldExample: View {
    @State private var query = ""

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            ESearchField(Text("Search"), text: $query, clearLabel: Text("Clear search"))
            Text(verbatim: "Query length: \(query.count)")
        }
    }
}
#endif
