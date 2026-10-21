import Foundation

/// 日志导出门面：把日志目录（活跃 + 轮转归档）打包成 zip，返回 URL 供分享。
///
/// 目录优先取 `AppLog.directoryURL`（bootstrap 后）；未 bootstrap 时回退 `Library/Logs`。
public enum LogExport {
    /// 当前用于导出的日志目录。
    public static var logDirectory: URL {
        if let dir = AppLog.directoryURL {
            return dir
        }
        let base = FileManager.default.urls(for: .libraryDirectory, in: .userDomainMask)[0]
        return base.appendingPathComponent("Logs", isDirectory: true)
    }

    /// 导出错误。
    public enum ExportError: Error, LocalizedError {
        case noLogs
        case zipFailed

        public var errorDescription: String? {
            switch self {
            case .noLogs: "暂无日志可导出"
            case .zipFailed: "日志打包失败"
            }
        }
    }

    /// 生成默认 zip 文件名（不含 `.zip`），如 `MyApp-20260812153022`。
    public static func makeFileName(prefix: String, date: Date = Date()) -> String {
        let formatter = DateFormatter()
        formatter.locale = Locale(identifier: "en_US_POSIX")
        formatter.timeZone = TimeZone.current
        formatter.dateFormat = "yyyyMMddHHmmss"
        let stamp = formatter.string(from: date)
        let safe = prefix
            .replacingOccurrences(of: "/", with: "-")
            .replacingOccurrences(of: " ", with: "-")
        return "\(safe)-\(stamp)"
    }

    /// 把日志目录打包成 zip，返回临时 zip 文件 URL。
    ///
    /// 导出会先 `AppLog.flush`，尽量带上最新缓冲行。
    /// 用 `NSFileCoordinator` 的 `.forUploading`——系统原生把目录压成 zip，零第三方依赖。
    /// - Parameter fileName: zip 文件名（不含 `.zip` 后缀），如 `myapp-v1.0-202606181630`。
    public static func exportZip(fileName: String) throws -> URL {
        AppLog.flush(timeout: 2.0)

        let dir = logDirectory
        let contents = (try? FileManager.default.contentsOfDirectory(atPath: dir.path)) ?? []
        guard !contents.isEmpty else { throw ExportError.noLogs }

        let coordinator = NSFileCoordinator()
        var coordError: NSError?
        var resultURL: URL?
        coordinator.coordinate(readingItemAt: dir, options: [.forUploading], error: &coordError) { zippedURL in
            let dest = FileManager.default.temporaryDirectory.appendingPathComponent("\(fileName).zip")
            try? FileManager.default.removeItem(at: dest)
            try? FileManager.default.copyItem(at: zippedURL, to: dest)
            resultURL = dest
        }
        if coordError != nil { throw ExportError.zipFailed }
        guard let url = resultURL, FileManager.default.fileExists(atPath: url.path) else {
            throw ExportError.zipFailed
        }
        return url
    }
}
