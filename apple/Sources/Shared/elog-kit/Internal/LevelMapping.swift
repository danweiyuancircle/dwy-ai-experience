import Puppy

/// 将自有 `AppLogLevel` 投递到 Puppy。
enum LevelMapping {
    static func emit(
        _ puppy: Puppy,
        level: AppLogLevel,
        message: String,
        category: String,
        file: String,
        function: String,
        line: UInt
    ) {
        switch level {
        case .debug:
            puppy.logMessage(
                .debug,
                message: message,
                tag: category,
                function: function,
                file: file,
                line: line,
                swiftLogInfo: ["source": "LogKit"]
            )
        case .info:
            puppy.logMessage(
                .info,
                message: message,
                tag: category,
                function: function,
                file: file,
                line: line,
                swiftLogInfo: ["source": "LogKit"]
            )
        case .warn:
            puppy.logMessage(
                .warning,
                message: message,
                tag: category,
                function: function,
                file: file,
                line: line,
                swiftLogInfo: ["source": "LogKit"]
            )
        case .error:
            puppy.logMessage(
                .error,
                message: message,
                tag: category,
                function: function,
                file: file,
                line: line,
                swiftLogInfo: ["source": "LogKit"]
            )
        }
    }
}
