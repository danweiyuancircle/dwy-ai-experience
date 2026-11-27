import SwiftUI
import DesignKitIOSPlayground

/// 独立入口：只承载组件目录，不影响 IOSControls 的 UITest 界面层级。
@main
struct IOSPlaygroundApp: App {
    var body: some Scene { WindowGroup { IOSPlayground() } }
}
