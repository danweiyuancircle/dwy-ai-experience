#if os(iOS)
import SwiftUI
import DesignKitIOS

/// 菜单项保留原生角色、分组和禁用语义。
struct MenuExample: View {
    @State private var count = 0

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            EMenu {
                Button("First action") { count += 1 }
                Button("Disabled action") {}.disabled(true)
                Divider()
                Button("Dangerous action", role: .destructive) { count += 1 }
            } label: {
                Label("More actions", systemImage: "ellipsis.circle")
            }
            Text(verbatim: "Action count: \(count)")
        }
    }
}
#endif
