#if os(macOS)
import SwiftUI

enum EListMove {
    static func indices(from source: IndexSet, to destination: Int, count: Int) -> (source: Int, target: Int)? {
        guard source.count == 1, let from = source.first, (0..<count).contains(from) else { return nil }
        let target = destination > from ? destination - 1 : destination
        guard (0..<count).contains(target), target != from else { return nil }
        return (from, target)
    }
}

/// 原生可排序列表及等效键盘/辅助功能动作；ID 须稳定唯一，顺序由宿主保存。
public struct EReorderableList<Item: Identifiable, Row: View>: View {
    @Environment(\.eControlTheme) private var theme
    private let items: [Item]
    private let reorderLabel: String
    private let moveUpLabel: String
    private let moveDownLabel: String
    private let onMove: (Item.ID, Item.ID) -> Bool
    private let row: (Item) -> Row

    public init(items: [Item], reorderLabel: String, moveUpLabel: String, moveDownLabel: String,
                onMove: @escaping (Item.ID, Item.ID) -> Bool, @ViewBuilder row: @escaping (Item) -> Row) {
        self.items = items
        self.reorderLabel = reorderLabel
        self.moveUpLabel = moveUpLabel
        self.moveDownLabel = moveDownLabel
        self.onMove = onMove
        self.row = row
    }

    public var body: some View {
        List {
            ForEach(items) { item in
                HStack(spacing: theme.spacing.group) {
                    Image(systemName: "line.3.horizontal")
                        .foregroundStyle(theme.colors.tertiaryText)
                        .frame(width: theme.toolbarGlyph).frame(minHeight: theme.fieldHeight)
                        .accessibilityLabel(reorderLabel).help(reorderLabel)
                    row(item)
                }
                .contextMenu {
                    Button { move(item.id, offset: -1) } label: { Label(moveUpLabel, systemImage: "arrow.up") }
                        .disabled(items.first?.id == item.id)
                    Button { move(item.id, offset: 1) } label: { Label(moveDownLabel, systemImage: "arrow.down") }
                        .disabled(items.last?.id == item.id)
                }
                .accessibilityElement(children: .contain)
                .accessibilityActions {
                    Button(moveUpLabel) { move(item.id, offset: -1) }
                    Button(moveDownLabel) { move(item.id, offset: 1) }
                }
            }
            .onMove { source, destination in
                guard let move = EListMove.indices(from: source, to: destination, count: items.count) else { return }
                _ = onMove(items[move.source].id, items[move.target].id)
            }
        }
        .listStyle(.plain).scrollContentBackground(.hidden)
    }

    private func move(_ id: Item.ID, offset: Int) {
        guard let index = items.firstIndex(where: { $0.id == id }), items.indices.contains(index + offset) else { return }
        _ = onMove(id, items[index + offset].id)
    }
}
#endif
