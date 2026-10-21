import Foundation
import CoreKit

// MARK: - ③ BizFoundation（业务基础层）
// 模块名即 BizFoundation；类型勿再叫 BizFoundation，避免与模块同名冲突。

/// 业务基础层示例 API。按领域拆 `Session/`、`Models/` 等子目录扩展。
public enum DomainFacade {
    /// 冒烟：模块可链接。
    public static var ready: Bool { true }

    /// 示例：使用 ④ CoreKit。
    public static func formatDemoSeconds(_ seconds: Int) -> String {
        TimeFormat.mmss(seconds)
    }
}
