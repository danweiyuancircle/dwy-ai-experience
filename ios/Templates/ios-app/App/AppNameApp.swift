import SwiftUI
import DesignCore
import DesignKitIOS
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
        WindowGroup {
            RootView()
                .environment(localization)
                .environment(theme)
                .environment(store)
                .environment(\.locale, localization.locale)
                .preferredColorScheme(theme.preferredColorScheme)
                .onAppear { theme.applyOnLaunch() }
        }
    }
}
