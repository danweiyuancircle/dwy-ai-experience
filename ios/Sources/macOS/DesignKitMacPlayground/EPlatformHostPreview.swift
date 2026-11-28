#if os(macOS)
import AppKit
import SwiftUI
import DesignKitMac

/// 平台桥接的独立演示；选择结果只显示路径，不创建书签、不读取文件也不执行危险操作。
public struct EPlatformHostPreview: View {
    @State private var selectedPath: String?
    @State private var window: EToolWindow?

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
            EButton("Show tool window") {
                window?.close()
                let window = EToolWindow(title: "Shared tool window", size: NSSize(width: 400, height: 180))
                window.setContent {
                    EProgressPanelContent(title: Text("Preview only")) {
                        EButton("Close") { [weak window] in window?.close() }
                    }
                }
                self.window = window
                window.center()
                window.makeKeyAndOrderFront(nil)
            }
        }
        .onDisappear { window?.close(); window = nil }
    }
}
#endif
