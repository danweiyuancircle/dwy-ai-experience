import Foundation

/// 目录资源访问。示例源码来自 `Resources/Examples`，由 `Scripts/sync-examples.py` 从真实编译的 `Fixtures` 生成，
/// 避免展示代码与实际预览代码分叉。
public enum IOSPlaygroundCatalog {
    /// 与 `apple/CHANGELOG.md` 的 AppleAppKit 版本对齐；发版时一起更新。
    public static let version = "0.16.0"

    public enum ResourceError: Error, LocalizedError {
        case missing(String)

        public var errorDescription: String? {
            switch self {
            case .missing(let path): "Missing Playground resource: \(path)"
            }
        }
    }

    /// 缺失时抛错，不静默跳到其他组件。
    public static func exampleSource(for component: IOSPlaygroundComponent) throws -> String {
        guard let url = Bundle.module.url(forResource: component.fixtureName + ".swift", withExtension: "txt",
                                          subdirectory: "Examples") else {
            throw ResourceError.missing("Examples/" + component.fixtureName + ".swift.txt")
        }
        return try String(contentsOf: url, encoding: .utf8)
    }

    /// Fixture 用 `#if os(iOS)` 包裹以便在 macOS 上也能解析包；复制给用户的源码去掉最外层守卫，内层条件编译保留。
    public static func strippingPlatformGuard(_ source: String) -> String {
        var lines = source.components(separatedBy: "\n")
        let hasTrailingNewline = lines.last == ""
        if hasTrailingNewline { lines.removeLast() }
        guard lines.first == "#if os(iOS)", lines.last == "#endif" else { return source }
        lines.removeFirst()
        lines.removeLast()
        return lines.joined(separator: "\n") + (hasTrailingNewline ? "\n" : "")
    }
}
