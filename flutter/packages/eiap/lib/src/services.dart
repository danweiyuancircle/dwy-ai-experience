import 'adapters.dart';
import 'models.dart';
import 'plugin_adapters.dart';

/// 无界面的购买流程门面：业务层只面对本类与 `src/models.dart` 的模型。
///
/// 平台商店实现经构造注入（默认 [InAppPurchaseAdapter]），测试注入 Fake；
/// 本库不做后端验证——凭据原文由业务方送自家服务端确认后再授权益。
class DwyBilling {
  DwyBilling() : _adapter = InAppPurchaseAdapter();

  DwyBilling.withAdapter(this._adapter);

  final DwyBillingAdapter _adapter;

  /// 当前设备能否发起商店购买；不可用时业务方应隐藏购买入口。
  Future<bool> available() => _guard(_adapter.available);

  /// 批量查询商品；只包含商店确认存在的商品。
  Future<List<DwyProduct>> products(Set<String> ids) =>
      _guard(() => _adapter.products(ids));

  /// 发起一次性买断购买，结果经 [updates] 流送达。
  Future<void> buy(String productId) => _guard(() => _adapter.buy(productId));

  /// 触发商店恢复并返回恢复流程期间收到的 restored 购买。
  Future<List<DwyPurchase>> restore() => _guard(_adapter.restore);

  /// 购买与恢复的状态流；必须持续监听以接住异步结果。
  Stream<DwyPurchase> get updates => _adapter.updates;

  /// 确认交付完成；只对 purchased / restored 的购买调用。
  Future<void> complete(DwyPurchase purchase) =>
      _guard(() => _adapter.complete(purchase));

  /// Adapter 已把平台异常折叠为 DwyBillingException；
  /// 这里只兜住穿透的平台异常（如插件直接抛出的 PlatformException），
  /// 避免陌生异常类型打破业务层的 catch 分支。
  Future<T> _guard<T>(Future<T> Function() action) async {
    try {
      return await action();
    } on DwyBillingException {
      rethrow;
    } catch (error) {
      throw DwyBillingException('store_error', error.toString());
    }
  }
}
