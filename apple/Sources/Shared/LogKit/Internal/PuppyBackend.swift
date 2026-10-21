import Foundation
import Puppy

/// 内部后端：组装 Console + FileRotation，对外类型全部抹掉。
/// 约束：只在 LogKit internal 引用 Puppy；失败时返回 nil，bootstrap 不阻塞启动。
final class PuppyBackend: @unchecked Sendable {
    let config: LogConfig
    private let puppy: Puppy
    private let formatter = LogLineFormatter()

    init?(config: LogConfig) {
        self.config = config
        do {
            try FileManager.default.createDirectory(
                at: config.directoryURL,
                withIntermediateDirectories: true
            )
        } catch {
            return nil
        }

        var loggers: [any Loggerable] = []

        // 文件侧接 trace：级别过滤在门面，避免双重门槛。
        let rotation = RotationConfig(
            suffixExtension: .numbering,
            maxFileSize: config.maxFileSizeBytes,
            maxArchivedFilesCount: UInt8(config.maxArchivedFilesCount)
        )
        if let fileLogger = try? FileRotationLogger(
            "\(config.subsystem).file",
            logLevel: .trace,
            logFormat: formatter,
            fileURL: config.fileURL,
            filePermission: "600",
            rotationConfig: rotation
        ) {
            loggers.append(fileLogger)
        }

        if config.alsoLogToConsole {
            let console = ConsoleLogger(
                "\(config.subsystem).console",
                logLevel: .trace,
                logFormat: formatter
            )
            loggers.append(console)
        }

        guard !loggers.isEmpty else { return nil }
        self.puppy = Puppy(loggers: loggers)
    }

    func log(
        level: AppLogLevel,
        message: String,
        category: String,
        file: String,
        function: String,
        line: UInt
    ) {
        LevelMapping.emit(
            puppy,
            level: level,
            message: message,
            category: category,
            file: file,
            function: function,
            line: line
        )
    }

    /// 等待底层异步队列刷完；测试与关键路径用。
    func flush(timeout: Double = 3.0) {
        _ = puppy.flush(timeout)
    }
}
