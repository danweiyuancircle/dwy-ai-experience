#if os(macOS)
import XCTest
import AppKit
import SwiftUI
@testable import DesignKitMac

@MainActor
final class MacSuggestionListTests: XCTestCase {
    func testMarkedTextKeepsNavigationWithTheInputMethod() {
        let editor = NSTextView()
        editor.setMarkedText("pin", selectedRange: NSRange(location: 3, length: 0),
                             replacementRange: NSRange(location: NSNotFound, length: 0))
        XCTAssertTrue(ESuggestionList.isComposing(editor))
        editor.unmarkText()
        XCTAssertFalse(ESuggestionList.isComposing(editor))
    }

    func testFilteringPreservesOrderAndDeduplicatesWithoutChangingInput() {
        XCTAssertEqual(ESuggestionList.values(["Android", "ADBox", "Android", "Safari"], query: "ad"), ["ADBox"])
        XCTAssertEqual(ESuggestionList.values(["a", "a", "b"], query: ""), ["a", "b"])
        XCTAssertEqual(ESuggestionList.values(["输入法", "显示"], query: " 输入 "), ["输入法"])
    }

    func testNativeComboDisablesCompletionAndOwnsPopup() {
        let coordinator = makeCoordinator()
        let combo = coordinator.makeControl()
        XCTAssertFalse(combo.completes)
        XCTAssertTrue(combo.usesDataSource)
        XCTAssertTrue(combo.hasVerticalScroller)
        XCTAssertTrue(combo.cell is NSComboBoxCell)
        XCTAssertTrue(combo.target === coordinator)
        let reference = NSComboBox()
        let container = NSView(frame: NSRect(x: 0, y: 0, width: 320, height: 100))
        combo.frame = NSRect(x: 0, y: 0, width: 300, height: 28)
        reference.frame = NSRect(x: 0, y: 40, width: 300, height: 28)
        container.addSubview(combo)
        container.addSubview(reference)
        let window = NSWindow(contentRect: container.frame, styleMask: [.titled], backing: .buffered, defer: false)
        window.contentView = container
        container.layoutSubtreeIfNeeded()
        // 离屏环境可能返回 AXUnknown；只验证未覆盖原生语义，完整 AX 树须在前台验收。
        XCTAssertEqual(combo.accessibilityRole(), reference.accessibilityRole())
    }

    func testBlurDoesNotCommitAndExplicitActivationCommitsOnce() {
        var input = " original "
        var commits: [String] = []
        var endings: [String] = []
        let parent = ENativeComboBox(title: "History", text: Binding(get: { input }, set: { input = $0 }),
                                      suggestions: [], onEditingEnded: { endings.append($0) },
                                      onCommit: { commits.append($0) })
        let coordinator = ENativeComboBox.Coordinator(parent)
        let combo = coordinator.makeControl()
        combo.stringValue = " typed "
        coordinator.controlTextDidChange(Notification(name: NSControl.textDidChangeNotification, object: combo))
        XCTAssertEqual(input, " typed ")
        XCTAssertTrue(commits.isEmpty)
        coordinator.controlTextDidEndEditing(Notification(name: NSControl.textDidEndEditingNotification, object: combo))
        XCTAssertEqual(endings, [" typed "])
        XCTAssertTrue(commits.isEmpty)
        coordinator.activate(combo)
        XCTAssertEqual(commits, [" typed "])
        combo.isEnabled = false
        coordinator.activate(combo)
        XCTAssertEqual(commits, [" typed "])
    }

    func testCandidateReorderPreservesIdentityAndRemovalDoesNotSubmitOrRewrite() {
        var commits: [String] = []
        var input = ""
        var parent = ENativeComboBox(title: "History", text: Binding(get: { input }, set: { input = $0 }),
                                      suggestions: ["First", "Second"], onEditingEnded: { _ in },
                                      onCommit: { commits.append($0) })
        let coordinator = ENativeComboBox.Coordinator(parent)
        let combo = coordinator.makeControl()
        coordinator.updateCandidates(combo)
        combo.selectItem(at: 1)
        parent = ENativeComboBox(title: "History", text: parent.$text,
                                  suggestions: ["Second", "First"], onEditingEnded: { _ in }, onCommit: { commits.append($0) })
        coordinator.parent = parent
        coordinator.updateCandidates(combo)
        XCTAssertEqual(combo.indexOfSelectedItem, 0)
        coordinator.parent = ENativeComboBox(title: "History", text: parent.$text,
                                              suggestions: [], onEditingEnded: { _ in }, onCommit: { commits.append($0) })
        coordinator.updateCandidates(combo)
        XCTAssertEqual(combo.indexOfSelectedItem, -1)
        XCTAssertTrue(commits.isEmpty)
        XCTAssertEqual(input, "")
    }

    private func makeCoordinator() -> ENativeComboBox.Coordinator {
        ENativeComboBox.Coordinator(ENativeComboBox(title: "History", text: .constant(""),
                                                       suggestions: [], onEditingEnded: { _ in }, onCommit: { _ in }))
    }
}
#endif
