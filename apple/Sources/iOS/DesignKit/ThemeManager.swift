import SwiftUI
import DesignCore
#if canImport(UIKit)
import UIKit
#endif

/// iOS 外观主题切换中枢。
///
/// 不用 `@AppStorage` 驱动 `.preferredColorScheme`（框架已知不即时刷新）。
/// 根视图 `@State` 持有本实例，属性变化可靠重算。
///
/// 除驱动 SwiftUI `.preferredColorScheme`，还同步
/// `UIWindow.overrideUserInterfaceStyle`，覆盖 alert / sheet / 键盘等 UIKit 弹层。
@MainActor
@Observable
public final class ThemeManager {
    public static let shared = ThemeManager()

    private static let key = "appearance.themeMode"

    /// 当前外观档位。写入即持久化并同步 window override。
    public var mode: ThemeMode {
        didSet {
            UserDefaults.standard.set(mode.rawValue, forKey: Self.key)
            applyToWindows()
        }
    }

    /// 给根视图 `.preferredColorScheme` 用；与 macOS API 对齐。
    /// iOS 上 system → nil（`overrideUserInterfaceStyle = .unspecified`）即可。
    public var preferredColorScheme: ColorScheme? {
        mode.colorScheme
    }

    /// 默认跟随系统；可按产品改。
    private init() {
        let saved = UserDefaults.standard.string(forKey: Self.key)
        mode = saved.flatMap(ThemeMode.init(rawValue:)) ?? .system
    }

    /// 把当前档位同步到所有前台 window。
    public func applyToWindows() {
        #if canImport(UIKit)
        let style: UIUserInterfaceStyle
        switch mode {
        case .system: style = .unspecified
        case .light: style = .light
        case .dark: style = .dark
        }
        for scene in UIApplication.shared.connectedScenes {
            guard let windowScene = scene as? UIWindowScene else { continue }
            for window in windowScene.windows {
                window.overrideUserInterfaceStyle = style
            }
        }
        #endif
    }

    /// app 启动、window 就绪后调用，补一次 override（init 时 window 多半还没建好）。
    public func applyOnLaunch() {
        applyToWindows()
    }
}
