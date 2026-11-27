#if os(iOS)
import SwiftUI
import DesignKitIOS

/// 用户原文用 Text(verbatim:)，避免被当作本地化 key。
struct LabelValueExample: View {
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            ELabelValue { Text("Original text") } value: { Text(verbatim: "line one\nline two") }
            ELabelValue { Text("Identifier") } value: { Text(verbatim: "designkit.ios.label-value") }
        }
    }
}
#endif
