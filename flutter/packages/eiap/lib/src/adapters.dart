import 'models.dart';

/// 商店对接的抽象边界；换商店实现时只新增本接口的实现类。
///
/// 实现约束：
/// - 所有方法的失败统一抛 [DwyBillingException]，不把平台异常类型漏给调用方。
/// - `buy` 只负责发起；购买结果（含用户取消）一律经 `updates` 流送达。
abstract class DwyBillingAdapter {
  /// 当前设备能否发起商店购买（未登录商店账号也可能返回 true）。
  Future<bool> available();

  /// 批量查询商品；只返回商店确认存在的商品，业务方自行核对数量。
  Future<List<DwyProduct>> products(Set<String> ids);

  /// 发起一次性买断购买。发起被商店拒绝或用户取消时抛
  /// [DwyBillingException]；成功发起后结果经 `updates` 流送达。
  Future<void> buy(String productId);

  /// 向商店请求恢复历史购买，返回恢复流程期间收到的 restored 购买。
  Future<List<DwyPurchase>> restore();

  /// 购买与恢复的状态流；业务方必须持续监听以处理 pending 等异步结果。
  Stream<DwyPurchase> get updates;

  /// 确认已完成交付（finish transaction / acknowledge）。
  /// 只允许对 purchased / restored 的购买调用，避免丢掉 pending 结果。
  Future<void> complete(DwyPurchase purchase);
}
