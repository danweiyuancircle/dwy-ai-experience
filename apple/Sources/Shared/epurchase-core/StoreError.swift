import Foundation
import L10nKit

/// 购买流程在系统边界上的失败。用户取消不走这里。
/// 宿主可通过 xcstrings 覆盖文案，缺少译文时仍提供可读提示。
public enum StoreError: LocalizedError, Sendable {
    /// 商品列表空，或 ASC 未挂此 product。
    case productUnavailable
    /// JWS 校验未过。
    case unverified
    /// 待家长审批等，尚未到账。
    case pending

    public var errorDescription: String? {
        switch self {
        case .productUnavailable:
            message("store_err_product_unavailable", fallback: "This product is unavailable.")
        case .unverified:
            message("store_err_unverified", fallback: "The App Store transaction could not be verified.")
        case .pending:
            message("store_err_pending", fallback: "This purchase is waiting for approval.")
        }
    }

    private func message(_ key: String, fallback: String) -> String {
        let translation = loc(String.LocalizationValue(key))
        return translation == key ? fallback : translation
    }
}
