import Foundation

extension Data {
    /// 从 hex 字符串构造 Data；含非法字符或奇数长度时返回 nil。
    public init?(hexString: String) {
        guard hexString.count % 2 == 0 else { return nil }
        let chars = Array(hexString)
        var data = Data(capacity: chars.count / 2)
        var i = 0
        while i < chars.count {
            guard let byte = UInt8(String(chars[i ... i + 1]), radix: 16) else { return nil }
            data.append(byte)
            i += 2
        }
        self = data
    }
}
