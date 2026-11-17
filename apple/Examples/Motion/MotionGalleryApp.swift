import SwiftUI
import DesignCore

/// 两端共用的原生动效示例；只修改本地展示状态，不访问设备、账户或用户数据。
@main
struct MotionGalleryApp: App {
    var body: some Scene {
        WindowGroup("DesignCore Motion") {
            MotionExample().frame(minWidth: 320, minHeight: 420)
        }
    }
}

private struct MotionExample: View {
    @State private var items = ["Files", "Images", "Tools"]
    @State private var showMessage = false
    @State private var hovered = false
    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                Text("Native motion").font(.title.bold())
                Text("Reduce Motion: \(reduceMotion ? "On" : "Off")")
                    .font(.caption).foregroundStyle(.secondary)
                Text("Change Reduce Motion in system Accessibility settings to compare the same interactions.")
                    .font(.caption).foregroundStyle(.secondary)
                Button("Reorder rows", systemImage: "arrow.up.arrow.down") {
                    items.reverse()
                }
                VStack(spacing: 8) {
                    ForEach(items, id: \.self) { item in
                        Text(item).frame(maxWidth: .infinity, alignment: .leading)
                            .padding(12).background(.quaternary, in: RoundedRectangle(cornerRadius: 8))
                            .eTransition(.softMove)
                    }
                }
                .eMotion(.reorder, value: items)
                Button("Toggle feedback", systemImage: "checkmark.circle") { showMessage.toggle() }
                VStack(alignment: .leading) {
                    if showMessage {
                        Label("Example completed", systemImage: "checkmark.circle")
                            .padding(12).background(.quaternary, in: RoundedRectangle(cornerRadius: 8))
                            .eTransition(.softMove)
                    }
                }
                .frame(minHeight: 44, alignment: .top)
                .eMotion(.feedback, value: showMessage)
                Text("Hover with a pointer")
                    .padding(12).frame(maxWidth: .infinity)
                    .background(hovered ? Color.accentColor.opacity(0.12) : Color.clear,
                                in: RoundedRectangle(cornerRadius: 8))
                    .onHover { hovered = $0 }
                    .eMotion(.hover, value: hovered)
            }
            .buttonStyle(.bordered)
            .padding(24)
        }
    }
}
