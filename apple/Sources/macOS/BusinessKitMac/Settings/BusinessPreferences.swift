#if os(macOS)
import DesignCore
import DesignKitMac
import L10nKit
import SwiftUI

/// 应用可以把所选字号档保存到本机或自己的同步存储。
public enum BusinessTextSize: String, CaseIterable, Identifiable, Sendable {
    case standard
    case large
    case extraLarge

    public var id: String { rawValue }

    /// 保留应用原有的品牌和布局。较大字号从应用给定的正文基线派生。
    public func applying(to theme: EControlTheme) -> EControlTheme {
        let increase: CGFloat
        switch self {
        case .standard: return theme
        case .large: increase = 2
        case .extraLarge: increase = 4
        }
        var theme = theme
        theme.typography = ETypography(bodySize: theme.typography.nativeBodySize + increase)
        return theme
    }

    var title: Text {
        switch self {
        case .standard: Text("Standard", tableName: "Settings", bundle: .module)
        case .large: Text("Large", tableName: "Settings", bundle: .module)
        case .extraLarge: Text("Extra Large", tableName: "Settings", bundle: .module)
        }
    }
}

/// 默认的通用设置。应用跨窗口共用一个实例，语言和外观沿用已有管理器。
@MainActor @Observable
public final class BusinessPreferences {
    public let localization = LocalizationManager.shared
    public let appearance = ThemeManager.shared
    private let defaults: UserDefaults
    private let textSizeKey: String

    /// 字号档写入后立即影响使用 `businessPreferences(_:theme:)` 的视图。
    public var textSize: BusinessTextSize {
        didSet { defaults.set(textSize.rawValue, forKey: textSizeKey) }
    }

    /// `defaults` 用于字号档。语言和外观由各自管理器持有。
    public init(
        defaults: UserDefaults = .standard,
        textSizeKey: String = "business.appearance.textSize"
    ) {
        self.defaults = defaults
        self.textSizeKey = textSizeKey
        textSize = defaults.string(forKey: textSizeKey).flatMap(BusinessTextSize.init(rawValue:)) ?? .standard
    }

    /// 获取应用当前字号对应的共享主题。
    public func controlTheme(from base: EControlTheme) -> EControlTheme {
        textSize.applying(to: base)
    }
}

public extension View {
    /// 在每个独立 Scene 或 AppKit 宿主根节点注入同一个偏好实例和应用主题。
    @MainActor
    func businessPreferences(_ preferences: BusinessPreferences, theme: EControlTheme = .standard) -> some View {
        let resolvedTheme = preferences.controlTheme(from: theme)
        return environment(\.locale, preferences.localization.locale)
            .environment(preferences.localization)
            .environment(preferences.appearance)
            .font(resolvedTheme.typography.body)
            .eControlTheme(resolvedTheme)
            .preferredColorScheme(preferences.appearance.preferredColorScheme)
            .onAppear { preferences.appearance.applyAppAppearance() }
    }
}
#endif
