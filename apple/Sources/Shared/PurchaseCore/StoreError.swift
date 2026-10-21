import Foundation
import L10nKit

/// 购买流程在系统边界上的失败。用户取消不走这里。
/// 文案 key 由宿主 App 的 xcstrings 提供（模板已带）。
public enum StoreError: LocalizedError, Sendable {
    /// 商品列表空，或 ASC 未挂此 product。
    case productUnavailable
    /// JWS 校验未过。
    case unverified
    /// 待家长审批等，尚未到账。
    case pending

    public var errorDescription: String? {
        switch self {
        case .productUnavailable: loc("store_err_product_unavailable")
        case .unverified: loc("store_err_unverified")
        case .pending: loc("store_err_pending")
        }
    }
}
