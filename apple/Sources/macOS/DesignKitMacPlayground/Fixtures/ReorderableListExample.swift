#if os(macOS)
import SwiftUI
import DesignKitMac

struct ReorderableListExample: View {
    private struct Entry: Identifiable { let id: String }
    var body: some View {
        EReorderableList(items: [Entry(id: "one"), Entry(id: "two")], reorderLabel: "Reorder", moveUpLabel: "Move up", moveDownLabel: "Move down", onMove: { _, _ in false }) { Text($0.id) }.frame(height: 160)
    }
}
#endif
