import Foundation

/// 带 category 的子 logger；类型完全自有，不暴露底层 Logger。
public struct AppLogger: Sendable {
    private let category: String

    /// - Parameter category: 短名（如 `timer` / `store`），写入行内 `[category]`。
    init(category: String) {
        self.category = category
    }

    public func debug(
        _ message: @autoclosure () -> String,
        file: StaticString = #fileID,
        function: StaticString = #function,
        line: UInt = #line
    ) {
        AppLog.write(
            level: .debug,
            message: { message() },
            category: category,
            file: file,
            function: function,
            line: line
        )
    }

    public func info(
        _ message: @autoclosure () -> String,
        file: StaticString = #fileID,
        function: StaticString = #function,
        line: UInt = #line
    ) {
        AppLog.write(
            level: .info,
            message: { message() },
            category: category,
            file: file,
            function: function,
            line: line
        )
    }

    public func warn(
        _ message: @autoclosure () -> String,
        file: StaticString = #fileID,
        function: StaticString = #function,
        line: UInt = #line
    ) {
        AppLog.write(
            level: .warn,
            message: { message() },
            category: category,
            file: file,
            function: function,
            line: line
        )
    }

    public func error(
        _ message: @autoclosure () -> String,
        file: StaticString = #fileID,
        function: StaticString = #function,
        line: UInt = #line
    ) {
        AppLog.write(
            level: .error,
            message: { message() },
            category: category,
            file: file,
            function: function,
            line: line
        )
    }
}
