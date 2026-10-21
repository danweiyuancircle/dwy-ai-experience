import Foundation

/// 时长格式化工具。Domain / UI 共用，避免散落 `String(format:)`。
public enum TimeFormat {
    /// 将秒数格式化为 `MM:SS`（向下取整到秒，负值按 0）。
    /// - Parameter seconds: 剩余或已用秒数。
    /// - Returns: 两位分 + 两位秒，如 `25:00`、`04:05`。
    public static func mmss(_ seconds: Int) -> String {
        let sec = max(0, seconds)
        let m = sec / 60
        let s = sec % 60
        return String(format: "%02d:%02d", m, s)
    }
}
