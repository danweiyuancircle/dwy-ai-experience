import SwiftUI
import L10nKit

/// 外观主题档位。持久化用 `rawValue`。
/// 黑 / 白 / 跟随系统。平台侧 `ThemeManager` 负责落到 UIKit / AppKit。
public enum ThemeMode: String, CaseIterable, Identifiable, Sendable {
    case system
    case light
    case dark

    public var id: String { rawValue }

    /// 映射到 `.preferredColorScheme`；`system` 为 nil。
    public var colorScheme: ColorScheme? {
        switch self {
        case .system: nil
        case .light: .light
        case .dark: .dark
        }
    }

    /// 设置页 SF Symbol。
    public var symbolName: String {
        switch self {
        case .system: "circle.lefthalf.filled"
        case .light: "sun.max.fill"
        case .dark: "moon.fill"
        }
    }

    /// 设置页展示名；依赖 L10n 资源 key（模板已带默认文案）。
    public var displayName: String {
        switch self {
        case .system: loc("theme_system")
        case .light: loc("theme_light")
        case .dark: loc("theme_dark")
        }
    }
}
