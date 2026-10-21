import Foundation

/// LogKit 全部运行时配置：默认值内聚本模块，上层 bootstrap 时可整包覆盖。
/// 约束：不放业务配置；子系统名 / 文件名由 App 注入，避免写死产品名。
public struct LogConfig: Sendable {
    /// 最低输出级别；低于此级的调用直接丢弃（不拼字符串、不落盘）。
    public var minimumLevel: AppLogLevel
    /// 日志目录；默认 `~/Library/Logs/<subsystem>/`。
    public var directoryURL: URL
    /// 当前写入文件名；默认 `app.log`。
    public var fileName: String
    /// 单文件字节上限；超过触发轮转。
    public var maxFileSizeBytes: UInt64
    /// 归档文件份数上限（不含当前写入文件）。
    public var maxArchivedFilesCount: Int
    /// 是否同时输出控制台。
    public var alsoLogToConsole: Bool
    /// 子系统标识，作底层 logger label 前缀与默认目录名。
    public var subsystem: String

    /// - Parameters:
    ///   - subsystem: 必填，如 `com.dwy.myapp`；决定默认日志目录段。
    ///   - minimumLevel: 默认随编译配置：DEBUG→debug，Release→info。
    ///   - directoryURL: 默认 `Library/Logs/<subsystem>/`。
    ///   - fileName: 默认 `app.log`。
    ///   - maxArchivedFilesCount: 须在 0...255（底层 UInt8）。
    public init(
        subsystem: String,
        minimumLevel: AppLogLevel = LogConfig.defaultMinimumLevel,
        directoryURL: URL? = nil,
        fileName: String = "app.log",
        maxFileSizeBytes: UInt64 = 2 * 1024 * 1024,
        maxArchivedFilesCount: Int = 5,
        alsoLogToConsole: Bool = LogConfig.defaultAlsoLogToConsole
    ) {
        self.subsystem = subsystem
        self.minimumLevel = minimumLevel
        self.directoryURL = directoryURL ?? LogConfig.directoryURL(forSubsystem: subsystem)
        self.fileName = fileName
        self.maxFileSizeBytes = maxFileSizeBytes
        self.maxArchivedFilesCount = max(0, min(maxArchivedFilesCount, 255))
        self.alsoLogToConsole = alsoLogToConsole
    }

    /// 骨架自测默认配置（非业务产品名）。
    public static var `default`: LogConfig {
        LogConfig(subsystem: "com.dwy.apple-app-kit", fileName: "app.log")
    }

    /// 按 App 子系统快速构造（推荐启动路径）。
    public static func app(subsystem: String, fileName: String = "app.log") -> LogConfig {
        LogConfig(subsystem: subsystem, fileName: fileName)
    }

    /// DEBUG 构建输出 debug；Release 从 info 起，不输出 debug。
    public static var defaultMinimumLevel: AppLogLevel {
        #if DEBUG
        .debug
        #else
        .info
        #endif
    }

    /// DEBUG 默认同打控制台；Release 默认只落盘。
    public static var defaultAlsoLogToConsole: Bool {
        #if DEBUG
        true
        #else
        false
        #endif
    }

    /// `~/Library/Logs/<subsystem>/`；目录不存在时 bootstrap 会创建。
    public static func directoryURL(forSubsystem subsystem: String) -> URL {
        let base = FileManager.default.urls(for: .libraryDirectory, in: .userDomainMask).first
            ?? FileManager.default.temporaryDirectory
        return base
            .appendingPathComponent("Logs", isDirectory: true)
            .appendingPathComponent(subsystem, isDirectory: true)
    }

    /// 当前写入文件完整路径。
    public var fileURL: URL {
        directoryURL.appendingPathComponent(fileName, isDirectory: false)
    }
}
