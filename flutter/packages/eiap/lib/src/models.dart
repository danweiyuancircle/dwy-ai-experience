/// 跨商店统一的商品与购买结果模型。
///
/// 字段只保留业务需要的稳定子集：平台特有的折扣、订阅组等概念不进入本库，
/// 避免未来替换商店实现时模型被迫携带无关字段。
library;

/// 商店内可购买的一次性商品（买断）。
///
/// `displayPrice` 是商店已按用户地区格式化好的价格串，直接展示；
/// 不要在客户端自行做汇率换算或重排格式。
class DwyProduct {
  const DwyProduct({
    required this.id,
    required this.title,
    required this.description,
    required this.displayPrice,
  });

  /// 与商店后台配置一致的商品标识；业务方用它对应会员或额度档位。
  final String id;
  final String title;
  final String description;

  /// 商店格式化的本地化价格，如 "$2.99"、"¥6.00"。
  final String displayPrice;
}

/// 一次购买在商店侧的状态。
///
/// 与 `in_app_purchase` 的状态一一对应，替换商店实现时映射到这些值，
/// 不要把商店特有状态原样漏给业务层。
enum DwyPurchaseStatus {
  /// 已发起，商店尚未确认（可能等待用户输入密码或家长批准）。
  pending,

  /// 商店确认购买成功；凭据必须交业务后端验证后才授权益。
  purchased,

  /// 从商店恢复的历史购买。
  restored,

  /// 用户在商店流程中主动取消，没有扣款也没有凭据。
  canceled,

  /// 商店报告失败，原因见 [DwyPurchase.errorMessage]。
  error,
}

/// 一次购买的结果快照。
///
/// `verificationData` 是平台原始凭据（iOS 收据/JWS、Android purchase token），
/// **必须**交给业务后端向商店验证后再发放权益；本库不做任何验证，
/// 也不把凭据写入日志。
class DwyPurchase {
  const DwyPurchase({
    required this.productId,
    required this.status,
    this.purchaseId,
    this.verificationData,
    this.errorMessage,
  });

  final String productId;

  /// 平台交易标识（iOS transactionId / Android orderId），可能为空。
  final String? purchaseId;

  /// 平台原始凭据原文，仅 [DwyPurchaseStatus.purchased] / restored 时可用。
  final String? verificationData;
  final DwyPurchaseStatus status;

  /// [DwyPurchaseStatus.error] 时商店给出的原因描述，直接给业务层判断。
  final String? errorMessage;
}

/// 购买流程中本库定义的失败；未知平台错误统一折叠为 `store_error`。
class DwyBillingException implements Exception {
  const DwyBillingException(this.code, this.message);

  /// 固定取值：`store_unavailable`、`purchase_rejected`、`user_canceled`、
  /// `store_error`。业务层按 code 分支，不解析 message。
  final String code;
  final String message;

  @override
  String toString() => 'DwyBillingException($code, $message)';
}
