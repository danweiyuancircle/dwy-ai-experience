import Foundation

/// 对外日志级别。
/// 命名 `AppLogLevel`：避免与底层 Puppy 的 `LogLevel` 同名冲突。
/// 约束：仅四级；`warn` 对外命名，落盘标记为 `WARN`。
public enum AppLogLevel: Int, Sendable, Comparable {
    case debug = 0
    case info = 1
    case warn = 2
    case error = 3

    public static func < (lhs: AppLogLevel, rhs: AppLogLevel) -> Bool {
        lhs.rawValue < rhs.rawValue
    }

    /// 落盘 / 控制台行内标记（自有格式，不透传底层枚举名）。
    public var token: String {
        switch self {
        case .debug: "DEBUG"
        case .info: "INFO"
        case .warn: "WARN"
        case .error: "ERROR"
        }
    }
}
