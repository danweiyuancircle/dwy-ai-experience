import 'dart:async';

import 'package:flutter/services.dart' show PlatformException;
import 'package:in_app_purchase/in_app_purchase.dart';
import 'package:in_app_purchase_platform_interface/in_app_purchase_platform_interface.dart';

import 'adapters.dart';
import 'models.dart';

/// 基于 Flutter 官方 `in_app_purchase` 的商店实现，覆盖 App Store 与 Google Play。
///
/// 完成语义的平台约束：`completePurchase` 必须持有插件原始 `PurchaseDetails`
/// （iOS 要用原交易 finish），因此本 adapter 维护主订阅并缓存未完成的原始
/// 交易；业务层看到的 `DwyPurchase` 只是映射快照，不含平台对象。
class InAppPurchaseAdapter implements DwyBillingAdapter {
  /// [platform] 供测试注入 Fake；生产构造访问门面单例，由它完成
  /// 各商店平台实现（pigeon 注册发生在 instance getter）后再取平台实例。
  InAppPurchaseAdapter([InAppPurchasePlatform? platform])
    : _platform = platform ?? _connectDefault() {
    // 主订阅在构造时建立：商店实现是广播流，晚订阅会漏掉本会话已发生的事件；
    // 无监听者时向广播控制器 add 是空操作，常驻订阅没有额外开销。
    // 订阅引用随插件单例的流存活，本类无需持有或释放。
    _platform.purchaseStream.listen(_handle);
  }

  static InAppPurchasePlatform _connectDefault() {
    InAppPurchase.instance;
    return InAppPurchasePlatform.instance;
  }

  final InAppPurchasePlatform _platform;

  /// 未完成交付的原始交易，键为插件 purchaseID（缺省退回商品 id）；
  /// complete 后移除，同键新事件覆盖旧值。
  final Map<String, PurchaseDetails> _pendingDetails = {};
  final StreamController<DwyPurchase> _events =
      StreamController<DwyPurchase>.broadcast();

  @override
  Future<bool> available() => _platform.isAvailable();

  @override
  Future<List<DwyProduct>> products(Set<String> ids) async {
    final response = await _platform.queryProductDetails(ids);
    if (response.error != null) {
      throw DwyBillingException('store_error', response.error!.message);
    }
    return [
      for (final details in response.productDetails)
        DwyProduct(
          id: details.id,
          title: details.title,
          description: details.description,
          displayPrice: details.price,
        ),
    ];
  }

  @override
  Future<void> buy(String productId) async {
    // buyNonConsumable 需要完整 ProductDetails，发起前先按单品再查一次。
    final response = await _platform.queryProductDetails({productId});
    if (response.error != null) {
      throw DwyBillingException('store_error', response.error!.message);
    }
    final ProductDetails? details = response.productDetails
        .where((candidate) => candidate.id == productId)
        .firstOrNull;
    if (details == null) {
      throw DwyBillingException('product_missing', '商店不存在商品 $productId');
    }
    bool accepted;
    try {
      accepted = await _platform.buyNonConsumable(
        purchaseParam: PurchaseParam(productDetails: details),
      );
    } on PlatformException catch (error) {
      // 触发条件：部分商店/插件路径把用户取消作为发起异常抛出；
      // 常规取消仍以 updates 流的 canceled 状态为准。
      if (_isCancel(error)) {
        throw const DwyBillingException('user_canceled', '已取消购买');
      }
      rethrow;
    }
    if (!accepted) {
      throw const DwyBillingException('purchase_rejected', '商店拒绝了本次购买发起');
    }
  }

  @override
  Future<List<DwyPurchase>> restore() async {
    // 恢复结果经同一条流逐笔送达（restored 状态）；先订阅收集、再触发，
    // restorePurchases 的 Future 完成时恢复流程即结束。
    final collected = <DwyPurchase>[];
    final subscription = _events.stream.listen((purchase) {
      if (purchase.status == DwyPurchaseStatus.restored)
        collected.add(purchase);
    });
    try {
      await _platform.restorePurchases();
      // 事件沿「插件流 → 主订阅 → 本订阅」两段微任务派发；先排空微任务，
      // 再 cancel 收集器，否则返回空列表。
      await Future<void>.delayed(Duration.zero);
    } finally {
      await subscription.cancel();
    }
    return collected;
  }

  @override
  Stream<DwyPurchase> get updates => _events.stream;

  @override
  Future<void> complete(DwyPurchase purchase) async {
    final details = _pendingDetails.remove(
      purchase.purchaseId ?? purchase.productId,
    );
    // 缓存缺失视为已交付：进程重启后未完成的交易会由商店经流重发，
    // 届时会再次进入缓存并可完成；此处幂等返回，不当作错误。
    if (details == null) return;
    await _platform.completePurchase(details);
  }

  void _handle(List<PurchaseDetails> items) {
    for (final details in items) {
      if (details.status == PurchaseStatus.purchased ||
          details.status == PurchaseStatus.restored) {
        _pendingDetails[details.purchaseID ?? details.productID] = details;
      }
      _events.add(_map(details));
    }
  }

  DwyPurchase _map(PurchaseDetails details) => DwyPurchase(
    productId: details.productID,
    purchaseId: details.purchaseID,
    status: switch (details.status) {
      PurchaseStatus.pending => DwyPurchaseStatus.pending,
      PurchaseStatus.purchased => DwyPurchaseStatus.purchased,
      PurchaseStatus.restored => DwyPurchaseStatus.restored,
      PurchaseStatus.canceled => DwyPurchaseStatus.canceled,
      PurchaseStatus.error => DwyPurchaseStatus.error,
    },
    // 后端验证使用商店服务端侧凭据（iOS 收据/JWS、Android purchase token）；
    // 部分平台两份相同，server 侧为空时退回 local 侧。
    verificationData: details.verificationData.serverVerificationData.isEmpty
        ? details.verificationData.localVerificationData
        : details.verificationData.serverVerificationData,
    errorMessage: details.error?.message,
  );

  bool _isCancel(PlatformException error) =>
      error.code.toLowerCase().contains('cancel') ||
      error.message?.toLowerCase().contains('cancel') == true;
}
