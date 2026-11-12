#if os(macOS)
import SwiftUI
import AppKit

/// 字符串历史按文本身份保序；同名不同对象应使用原生强类型 Picker，而非此历史输入。
enum ESuggestionList {
    @MainActor
    static func isComposing(_ editor: NSTextView?) -> Bool { editor?.hasMarkedText() == true }

    static func values(_ values: [String], query: String) -> [String] {
        let query = query.trimmingCharacters(in: .whitespacesAndNewlines)
        var seen = Set<String>()
        return values.filter { seen.insert($0).inserted && (query.isEmpty || $0.localizedStandardContains(query)) }
    }


}

/// 原生建议输入：NSComboBox 拥有弹出窗口、滚动、屏幕边缘、VoiceOver 和输入法行为。
/// 自动补全始终关闭；只在明确激活时提交，失焦单独通知，不存历史。
public struct EComboBox: View {
    @Environment(\.eControlTheme) private var theme
    @Environment(\.locale) private var locale
    private let title: EComboTitle
    @Binding private var text: String
    private let suggestions: [String]
    private let onEditingEnded: (String) -> Void
    private let onCommit: (String) -> Void

    /// title 携带调用方 bundle；suggestions 为原文。取消、关闭和失焦不会调用 onCommit。
    public init(_ title: LocalizedStringResource, text: Binding<String>, suggestions: [String],
                onEditingEnded: @escaping (String) -> Void = { _ in }, onCommit: @escaping (String) -> Void) {
        self.title = .localized(title)
        self._text = text
        self.suggestions = suggestions
        self.onEditingEnded = onEditingEnded
        self.onCommit = onCommit
    }

    /// 动态原文标题显式退出本地化，不把用户内容当资源 key。
    public init(verbatim title: String, text: Binding<String>, suggestions: [String],
                onEditingEnded: @escaping (String) -> Void = { _ in }, onCommit: @escaping (String) -> Void) {
        self.title = .verbatim(title)
        self._text = text
        self.suggestions = suggestions
        self.onEditingEnded = onEditingEnded
        self.onCommit = onCommit
    }

    public var body: some View {
        ENativeComboBox(title: title.resolve(locale: locale), text: $text,
                                 suggestions: suggestions, onEditingEnded: onEditingEnded, onCommit: onCommit)
            .frame(minHeight: theme.searchHeight)
    }
}

private enum EComboTitle {
    case localized(LocalizedStringResource)
    case verbatim(String)

    func resolve(locale: Locale) -> String {
        switch self {
        case .localized(var resource):
            resource.locale = locale
            return String(localized: resource)
        case .verbatim(let value): return value
        }
    }
}

struct ENativeComboBox: NSViewRepresentable {
    @Environment(\.isEnabled) private var isEnabled
    @Environment(\.controlSize) private var controlSize
    let title: String
    @Binding var text: String
    let suggestions: [String]
    let onEditingEnded: (String) -> Void
    let onCommit: (String) -> Void

    func makeCoordinator() -> Coordinator { Coordinator(self) }

    func makeNSView(context: Context) -> NSComboBox {
        context.coordinator.makeControl()
    }

    func updateNSView(_ combo: NSComboBox, context: Context) {
        context.coordinator.parent = self
        combo.isEnabled = isEnabled
        switch controlSize {
        case .mini: combo.controlSize = .mini
        case .small: combo.controlSize = .small
        case .large, .extraLarge: combo.controlSize = .large
        default: combo.controlSize = .regular
        }
        combo.font = NSFont.preferredFont(forTextStyle: .body)
        combo.placeholderString = title
        combo.setAccessibilityLabel(title)
        let editor = combo.currentEditor() as? NSTextView
        // 标记文本属于输入法；SwiftUI 的回流与候选刷新不能中断正在组合的原文。
        guard !ESuggestionList.isComposing(editor) else { return }
        if combo.stringValue != text { combo.stringValue = text }
        context.coordinator.updateCandidates(combo)
    }

    @MainActor
    final class Coordinator: NSObject, NSComboBoxDataSource, NSComboBoxDelegate {
        var parent: ENativeComboBox
        private(set) var candidates: [String] = []

        init(_ parent: ENativeComboBox) { self.parent = parent }

        func makeControl() -> NSComboBox {
            let combo = NSComboBox()
            combo.completes = false
            combo.usesDataSource = true
            combo.hasVerticalScroller = true
            combo.numberOfVisibleItems = 8
            combo.delegate = self
            combo.dataSource = self
            combo.target = self
            combo.action = #selector(activate(_:))
            combo.setContentHuggingPriority(.defaultLow, for: .horizontal)
            return combo
        }


        func updateCandidates(_ combo: NSComboBox) {
            let values = ESuggestionList.values(parent.suggestions, query: combo.stringValue)
            guard candidates != values else { return }
            let selected = candidates.indices.contains(combo.indexOfSelectedItem) ? candidates[combo.indexOfSelectedItem] : nil
            candidates = values
            combo.reloadData()
            if let selected, let index = candidates.firstIndex(of: selected) {
                combo.selectItem(at: index)
            } else if combo.indexOfSelectedItem >= 0 {
                combo.deselectItem(at: combo.indexOfSelectedItem)
            }
        }

        func numberOfItems(in comboBox: NSComboBox) -> Int { candidates.count }
        func comboBox(_ comboBox: NSComboBox, objectValueForItemAt index: Int) -> Any? { candidates[index] }

        func controlTextDidChange(_ notification: Notification) {
            guard let combo = notification.object as? NSComboBox else { return }
            parent.text = combo.stringValue
            guard !ESuggestionList.isComposing(combo.currentEditor() as? NSTextView) else { return }
            updateCandidates(combo)
        }

        func controlTextDidEndEditing(_ notification: Notification) {
            guard let combo = notification.object as? NSComboBox else { return }
            parent.text = combo.stringValue
            parent.onEditingEnded(combo.stringValue)
        }

        @objc func activate(_ combo: NSComboBox) {
            guard combo.isEnabled, !ESuggestionList.isComposing(combo.currentEditor() as? NSTextView) else { return }
            parent.text = combo.stringValue
            parent.onCommit(combo.stringValue)
        }
    }
}
#endif
