import Foundation

/// 应用统一日志门面。
/// 对外只暴露本类型与 `LogConfig` / `AppLogLevel` / `AppLogger` / `LogExport`；
/// 不 import / 不返回 Puppy、swift-log 类型。
///
/// 使用：
/// ```swift
/// AppLog.bootstrap(config: .app(subsystem: "com.dwy.myapp"))
/// AppLog.info("启动完成")
/// AppLog.logger(category: "timer").debug("tick")
/// ```
public enum AppLog {
    /// 可变状态装进引用类型，满足 Swift 6 全局可变 Sendable 约束；访问仍用 lock。
    private final class State: @unchecked Sendable {
        var backend: PuppyBackend?
        var config: LogConfig?
    }

    private static let lock = NSLock()
    private static let state = State()

    /// 当前生效配置；未 bootstrap 为 nil。
    public static var currentConfig: LogConfig? {
        lock.lock(); defer { lock.unlock() }
        return state.config
    }

    /// 当前日志目录；未 bootstrap 为 nil。
    public static var directoryURL: URL? {
        currentConfig?.directoryURL
    }

    /// 进程内成功安装一次。
    /// - Returns: `true` 首次成功；已安装或底层初始化失败返回 `false`。
    @discardableResult
    public static func bootstrap(config: LogConfig = .default) -> Bool {
        lock.lock()
        defer { lock.unlock() }
        if state.backend != nil {
            return false
        }
        guard let installed = PuppyBackend(config: config) else {
            return false
        }
        state.backend = installed
        state.config = config
        return true
    }

    public static func debug(
        _ message: @autoclosure () -> String,
        file: StaticString = #fileID,
        function: StaticString = #function,
        line: UInt = #line
    ) {
        write(level: .debug, message: { message() }, category: "app", file: file, function: function, line: line)
    }

    public static func info(
        _ message: @autoclosure () -> String,
        file: StaticString = #fileID,
        function: StaticString = #function,
        line: UInt = #line
    ) {
        write(level: .info, message: { message() }, category: "app", file: file, function: function, line: line)
    }

    public static func warn(
        _ message: @autoclosure () -> String,
        file: StaticString = #fileID,
        function: StaticString = #function,
        line: UInt = #line
    ) {
        write(level: .warn, message: { message() }, category: "app", file: file, function: function, line: line)
    }

    public static func error(
        _ message: @autoclosure () -> String,
        file: StaticString = #fileID,
        function: StaticString = #function,
        line: UInt = #line
    ) {
        write(level: .error, message: { message() }, category: "app", file: file, function: function, line: line)
    }

    /// 带 category 的子 logger。
    public static func logger(category: String) -> AppLogger {
        AppLogger(category: category)
    }

    // MARK: - Internal

    /// 实际写入入口；级别过滤在此完成，保证未达级不求值 message 闭包。
    static func write(
        level: AppLogLevel,
        message: () -> String,
        category: String,
        file: StaticString,
        function: StaticString,
        line: UInt
    ) {
        lock.lock()
        let active = state.backend
        let minLevel = state.config?.minimumLevel
        lock.unlock()

        guard let active, let minLevel, level >= minLevel else { return }
        active.log(
            level: level,
            message: message(),
            category: category,
            file: String(describing: file),
            function: String(describing: function),
            line: line
        )
    }

    /// 等待异步写盘完成；导出日志前调用，保证最新行已落盘。
    public static func flush(timeout: Double = 3.0) {
        lock.lock()
        let active = state.backend
        lock.unlock()
        active?.flush(timeout: timeout)
    }

    /// 测试专用：清空 once 状态，允许再次 bootstrap。
    static func resetForTesting() {
        lock.lock()
        state.backend?.flush(timeout: 1.0)
        state.backend = nil
        state.config = nil
        lock.unlock()
    }

    /// 测试专用：等待异步写盘完成。
    static func flushForTesting(timeout: Double = 3.0) {
        flush(timeout: timeout)
    }
}
