import Foundation

/// 字节数紧凑格式化。把文件大小转成列表里短促易读的串。
///
/// 规则：小于 1KB 直接显字节带 B；否则按 K/M/G 单字母单位，整数省略小数、否则保留 1 位小数。
/// 示例：560 → "560B"、200K → "200K"、1.1G → "1.1G"。纯函数，可 `swift test`。
public enum ByteCount {
    /// 把字节数格式化为紧凑串。
    /// - Parameter bytes: 文件字节数。目录或解析失败时通常为 0，显示 "0B"。
    public static func compact(_ bytes: UInt32) -> String {
        compact(UInt64(bytes))
    }

    /// UInt64 重载，避免大文件截断。
    public static func compact(_ bytes: UInt64) -> String {
        let b = Double(bytes)
        let kb = 1024.0
        let mb = kb * 1024
        let gb = mb * 1024
        switch b {
        case ..<kb:
            return "\(Int(b))B"
        case ..<mb:
            return unitString(b / kb, "K")
        case ..<gb:
            return unitString(b / mb, "M")
        default:
            return unitString(b / gb, "G")
        }
    }

    /// 数值 + 单位：整数省小数（200K），否则 1 位小数（1.1G）。
    private static func unitString(_ value: Double, _ unit: String) -> String {
        value == value.rounded()
            ? "\(Int(value))\(unit)"
            : String(format: "%.1f%@", value, unit)
    }
}
