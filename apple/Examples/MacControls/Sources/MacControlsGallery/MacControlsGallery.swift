import AppKit
import SwiftUI
import DesignKitMacPlayground

/// 独立宿主只拥有窗口与激活；目录、说明和可运行示例与嵌入产品共用。
@main
struct MacControlsGallery: App {
    var body: some Scene {
        WindowGroup("Mac Controls") {
            EPlayground()
                .onAppear {
                    NSApp.setActivationPolicy(.regular)
                    NSApp.activate()
                }
        }
        .defaultSize(width: 1100, height: 800)
    }
}
