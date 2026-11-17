import Foundation
import Puppy

/// 自有落盘行格式。把底层 warning 显示成 WARN。
struct LogLineFormatter: LogFormattable {
    private let dateFormat: DateFormatter

    init() {
        let df = DateFormatter()
        df.locale = Locale(identifier: "en_US_POSIX")
        df.timeZone = TimeZone.current
        df.dateFormat = "yyyy-MM-dd'T'HH:mm:ss.SSSZZZZZ"
        self.dateFormat = df
    }

    func formatMessage(
        _ level: LogLevel,
        message: String,
        tag: String,
        function: String,
        file: String,
        line: UInt,
        swiftLogInfo: [String: String],
        label: String,
        date: Date,
        threadID: UInt64
    ) -> String {
        let levelToken: String
        switch level {
        case .debug: levelToken = "DEBUG"
        case .info: levelToken = "INFO"
        case .warning: levelToken = "WARN"
        case .error: levelToken = "ERROR"
        default: levelToken = level.description
        }
        let dateText = dateFormatter(date, withFormatter: dateFormat)
        let category = tag.isEmpty ? "-" : tag
        let shortFile = fileName(file)
        return "\(dateText) \(levelToken) [\(category)] \(shortFile)#L.\(line) \(message)"
    }
}
