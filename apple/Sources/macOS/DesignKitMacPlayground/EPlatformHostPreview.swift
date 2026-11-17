#if os(macOS)
import AppKit
import SwiftUI
import DesignKitMac

/// 平台桥接的独立演示；选择结果只显示路径，不创建书签、不读取文件也不执行危险操作。
public struct EPlatformHostPreview: View {
    @State private var selectedPath: String?
    @State private var panel: EToolPanel?

    public init() {}

    public var body: some View {
        VStack(alignment: .leading, spacing: ESpace.row) {
            EPageHeader(title: Text("Platform dialogs and windows"))
            EButton("Show confirmation") {
                let alert = EAlert(title: "Example confirmation", message: "No files will be changed.",
                                   actions: [.init("Continue"), .init("Cancel", role: .cancel)])
                _ = alert.runModal()
            }
            EButton("Choose a directory") {
                guard let selected = EFileDialog.chooseDirectory() else { return }
                selectedPath = selected.path
                selected.stopAccessingSecurityScopedResource()
            }
            if let selectedPath { Text(verbatim: selectedPath).textSelection(.enabled) }
            EButton("Show tool panel") {
                panel?.close()
                let panel = EToolPanel(title: "Shared tool panel", size: NSSize(width: 400, height: 180))
                panel.setContent {
                    EProgressPanelContent(title: Text("Preview only")) {
                        EButton("Close") { [weak panel] in panel?.close() }
                    }
                }
                self.panel = panel
                panel.center()
                panel.makeKeyAndOrderFront(nil)
            }
        }
        .onDisappear { panel?.close(); panel = nil }
    }
}
#endif
