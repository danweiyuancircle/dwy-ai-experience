import Foundation
import SwiftUI
import DesignCore
#if canImport(AppKit)
import AppKit
#endif

/// macOS 外观主题切换中枢。
///
/// 不用 `@AppStorage` 驱动 `.preferredColorScheme`（框架已知不即时刷新）。
/// 根视图 `@State` 持有本实例。
///
/// macOS 上 `preferredColorScheme` 往往不刷新 AppKit 动态色；
/// 必须同步 `NSApp.appearance` 才即时切换黑白。
///
/// **跟随系统**不能对 SwiftUI 传 `nil`：从 Light/Dark 回到 `nil` 时
/// 窗口常卡住旧方案。因此 `preferredColorScheme` 在 system 档解析为
/// 当前系统黑白，并监听 `AppleInterfaceThemeChangedNotification` 再解析。
@MainActor
@Observable
public final class ThemeManager {
    public static let shared = ThemeManager()

    private static let modeKey = "appearance.themeMode"
    private static let systemThemeChanged = Notification.Name("AppleInterfaceThemeChangedNotification")

    /// 当前主题档。写入即持久化并同步应用外观。
    public var mode: ThemeMode {
        didSet {
            UserDefaults.standard.set(mode.rawValue, forKey: Self.modeKey)
            scheduleApplyAppAppearance()
        }
    }

    /// 系统外观变更序号；`preferredColorScheme` 读取它以建立 Observation 依赖。
    /// mode == .system 时 OS 切换黑白会自增，驱动界面重算。
    public private(set) var systemAppearanceRevision: UInt = 0

    /// 给根视图 `.preferredColorScheme` 用。
    /// system 解析为当前系统值（不返回 nil），避免 Light→跟随 卡住浅色。
    public var preferredColorScheme: ColorScheme? {
        _ = systemAppearanceRevision
        switch mode {
        case .light: return .light
        case .dark: return .dark
        case .system: return Self.resolvedSystemColorScheme
        }
    }

    /// 持有 observer token；单例生命周期与进程一致，无需 remove。
    private var systemThemeObserver: NSObjectProtocol?

    /// 默认深色（菜单栏类产品常见）；产品可改默认或靠持久化覆盖。
    private init() {
        let saved = UserDefaults.standard.string(forKey: Self.modeKey)
        mode = saved.flatMap(ThemeMode.init(rawValue:)) ?? .dark
        scheduleApplyAppAppearance()
        startObservingSystemTheme()
    }

    /// 产品侧指定首启默认档；用户已有持久化选择时不生效。
    /// 在 App init 里调用一次。
    public func configureDefault(_ defaultMode: ThemeMode) {
        guard UserDefaults.standard.string(forKey: Self.modeKey) == nil else { return }
        mode = defaultMode
    }

    /// 延后到主线程下一拍，避免 App 启动前 `NSApp` 为 nil 崩溃。
    private func scheduleApplyAppAppearance() {
        DispatchQueue.main.async { [weak self] in
            self?.applyAppAppearance()
        }
    }

    #if canImport(AppKit)
    /// 系统菜单栏状态项窗口（私有类 `NSStatusBarWindow`）。
    /// 写 App 主题会让模板图跟 App 而不是跟菜单栏（壁纸明暗）；浅色菜单栏上图标变白。
    /// 不能用 `window.level == .statusBar`：业务 popover 也可能是这个 level。
    public static func isSystemStatusBarWindow(_ window: NSWindow) -> Bool {
        NSStringFromClass(type(of: window)).contains("StatusBarWindow")
    }
    #endif

    /// 把档位落到 `NSApp.appearance`，并清掉窗口级覆盖以免卡住。
    /// 跳过 `NSStatusBarWindow`：菜单栏图标必须跟菜单栏，不能跟 App 主题。
    public func applyAppAppearance() {
        #if canImport(AppKit)
        guard let app = NSApp else {
            scheduleApplyAppAppearance()
            return
        }
        let appearance: NSAppearance?
        switch mode {
        case .dark:
            appearance = NSAppearance(named: .darkAqua)
        case .light:
            appearance = NSAppearance(named: .aqua)
        case .system:
            // nil = 跟随系统；同时清窗口级 appearance，避免从强制浅/深色切回时粘住。
            appearance = nil
        }
        app.appearance = appearance
        for window in app.windows where !Self.isSystemStatusBarWindow(window) {
            window.appearance = appearance
        }
        #endif
    }

    // MARK: - System appearance

    /// 读系统偏好（不受当前 `NSApp.appearance` 覆盖影响）。
    private static var resolvedSystemColorScheme: ColorScheme {
        if UserDefaults.standard.string(forKey: "AppleInterfaceStyle") == "Dark" {
            return .dark
        }
        return .light
    }

    private func startObservingSystemTheme() {
        #if os(macOS)
        systemThemeObserver = DistributedNotificationCenter.default().addObserver(
            forName: Self.systemThemeChanged,
            object: nil,
            queue: .main
        ) { [weak self] _ in
            guard let self else { return }
            Task { @MainActor in
                self.handleSystemThemeChanged()
            }
        }
        #endif
    }

    private func handleSystemThemeChanged() {
        guard mode == .system else { return }
        systemAppearanceRevision &+= 1
        scheduleApplyAppAppearance()
    }
}
