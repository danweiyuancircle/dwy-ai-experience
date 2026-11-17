import Foundation

/// 项目统一错误身份标记。
/// 自定义错误 conform 它，与系统 / 三方错误区分，可 `catch is AppError` 兜底。
///
/// 有意保持标记协议（无 requirement）：UI 只消费文案 / 具体 case，
/// 不加分类·级别·可重试等推测性字段。
public protocol AppError: Error {}

/// 要在 UI 展示文案的错误：AppError + LocalizedError。
public protocol UserFacingError: AppError, LocalizedError {}
