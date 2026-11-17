#if os(macOS)
import SwiftUI
import DesignKitMac

/// 页面组合的独立演示；仅修改局部状态，不读写业务配置、文件或主题单例。
public struct ERecoveredCompositionsPreview: View {
    @Environment(\.locale) private var locale
    @State private var enabled = true
    @State private var name = "Example"
    @State private var saved = false
    @State private var items = [SampleItem(id: "first"), SampleItem(id: "second"), SampleItem(id: "third")]

    public init() {}

    public var body: some View {
        VStack(alignment: .leading, spacing: ESpace.section) {
            EPageHeader(title: text("Shared page compositions", "共享页面组合"),
                        subtitle: text("The same theme drives pages, rows and tools.", "页面、列表行与工具使用同一主题。"))
            EItemRow(isSelected: true) {
                EApplicationIcon(bundleIdentifier: "com.apple.Terminal", fallbackSymbol: "terminal")
                text("Application action", "应用操作")
                Spacer()
                ESwitch(text("Enabled", "启用"), isOn: $enabled)
            }
            ESidebarItem { Label { text("Sidebar item", "侧栏项") } icon: { Image(systemName: "folder") } }
            EForm {
                EField(text("Name", "名称")) { ETextField(text("Name", "名称"), text: $name) }
                ELabelValue(text("Current value", "当前值"), value: Text(verbatim: name))
            } actions: {
                EButton(emphasis: .primary, action: { saved = true }) { text("Save locally", "仅在示例中保存") }
            }
            .frame(height: 150)
            if saved {
                ENotice(text("Example state updated", "示例状态已更新"), tone: .success) { EmptyView() }
            }
            EReorderableList(items: items, reorderLabel: string("Drag to reorder", "拖动排序"),
                             moveUpLabel: string("Move up", "上移"), moveDownLabel: string("Move down", "下移"),
                             onMove: move) { item in
                Text(verbatim: item.id)
            }
            .frame(height: 130)
            EContentState(.empty, title: text("No results", "暂无结果"), systemImage: "folder") { EmptyView() }
            EProgressPanelContent(title: text("Processing", "正在处理"), fraction: EProgressFraction(0.5),
                                  hint: text("Cancellation belongs to the host task.", "取消由宿主任务处理。")) {
                EButton(action: { enabled = false }) { text("Cancel example", "取消示例") }
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
    }

    private func move(_ source: String, _ target: String) -> Bool {
        guard let from = items.firstIndex(where: { $0.id == source }),
              let to = items.firstIndex(where: { $0.id == target }) else { return false }
        items.move(fromOffsets: IndexSet(integer: from), toOffset: from < to ? to + 1 : to)
        return true
    }

    private func string(_ en: String, _ zh: String) -> String {
        locale.language.languageCode?.identifier == "zh" ? zh : en
    }

    private func text(_ en: String, _ zh: String) -> Text { Text(verbatim: string(en, zh)) }

    private struct SampleItem: Identifiable { let id: String }
}
#endif
