import SwiftUI
import DesignCore
import DesignKitMac
import L10nKit
import LogKit
import PurchaseCore
import BizFoundation

// MARK: - ① App 层
// 打包入口、启动顺序、全局 environment。功能页见 Features/。

@main
struct __APP_NAME__App: App {
    @State private var localization = LocalizationManager.shared
    @State private var theme = ThemeManager.shared
    @State private var store = LifetimeStore(productID: AppConfig.unlockProductID)

    init() {
        // 本地日志：单文件上限 + 归档份数 = 循环写，不无限涨盘。
        AppLog.bootstrap(
            config: LogConfig(
                subsystem: "__BUNDLE_ID__",
                fileName: "__APP_NAME__.log",
                maxFileSizeBytes: 2 * 1024 * 1024,
                maxArchivedFilesCount: 5
            )
        )
        AppLog.info("app launch")
        LocalizationManager.shared.configure(supported: [.system, .zhHans, .en])
    }

    var body: some Scene {
        Window("__APP_NAME__", id: "main") {
            RootView()
                .environment(localization)
                .environment(theme)
                .environment(store)
                .environment(\.locale, localization.locale)
                // 用 ThemeManager.preferredColorScheme：system 会解析成当前系统黑白，避免 nil 卡色。
                .preferredColorScheme(theme.preferredColorScheme)
        }
        .defaultSize(width: 420, height: 560)
    }
}
