#if os(macOS)
import AppKit
import SwiftUI

/// 本机应用图标；缺失应用使用显式符号，不扫描目录、联网或保存图标。
public struct EApplicationIcon: View {
    @Environment(\.eControlTheme) private var theme
    private let bundleIdentifier: String
    private let appPath: String?
    private let fallbackSymbol: String

    public init(bundleIdentifier: String, appPath: String? = nil, fallbackSymbol: String) {
        self.bundleIdentifier = bundleIdentifier
        self.appPath = appPath
        self.fallbackSymbol = fallbackSymbol
    }

    public var body: some View {
        Group {
            if let image = Self.image(bundleIdentifier: bundleIdentifier, appPath: appPath, fallbackSymbol: fallbackSymbol) {
                Image(nsImage: image).resizable().scaledToFit()
            }
        }
        .frame(width: theme.toolbarGlyph, height: theme.toolbarGlyph)
        .accessibilityHidden(true)
    }

    /// AppKit 查询在主线程执行；路径用于尚未注册到 Launch Services 的自定义应用。
    @MainActor
    public static func image(bundleIdentifier: String, appPath: String? = nil, fallbackSymbol: String) -> NSImage? {
        if let url = NSWorkspace.shared.urlForApplication(withBundleIdentifier: bundleIdentifier) {
            return NSWorkspace.shared.icon(forFile: url.path)
        }
        if let appPath, FileManager.default.fileExists(atPath: appPath) {
            return NSWorkspace.shared.icon(forFile: appPath)
        }
        return NSImage(systemSymbolName: fallbackSymbol, accessibilityDescription: nil)
    }
}
#endif
