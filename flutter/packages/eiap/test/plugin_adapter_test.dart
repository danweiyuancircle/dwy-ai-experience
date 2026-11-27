import 'dart:async';

import 'package:dwy_iap/dwy_iap.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:in_app_purchase_platform_interface/in_app_purchase_platform_interface.dart';

/// 记录调用的平台 Fake：验证 InAppPurchaseAdapter 的映射与缓存行为。
class FakePlatform extends InAppPurchasePlatform {
  FakePlatform();

  bool available = true;
  bool acceptBuy = true;
  ProductDetailsResponse queryResponse = ProductDetailsResponse(
    productDetails: const [],
    notFoundIDs: [],
  );
  List<PurchaseDetails> restoreResults = [];
  final StreamController<List<PurchaseDetails>> incoming =
      StreamController<List<PurchaseDetails>>.broadcast();
  int completeCount = 0;

  @override
  @override
  Future<bool> isAvailable() async => available;

  @override
  Future<ProductDetailsResponse> queryProductDetails(Set<String> ids) async =>
      queryResponse;

  @override
  Future<bool> buyNonConsumable({required PurchaseParam purchaseParam}) async =>
      acceptBuy;

  @override
  Future<void> completePurchase(PurchaseDetails purchase) async {
    completeCount++;
  }

  @override
  Future<void> restorePurchases({String? applicationUserName}) async {
    incoming.add(restoreResults);
  }

  @override
  Stream<List<PurchaseDetails>> get purchaseStream => incoming.stream;
}

PurchaseDetails event({
  required String productId,
  required PurchaseStatus status,
  String? purchaseId,
}) => PurchaseDetails(
  productID: productId,
  purchaseID: purchaseId,
  verificationData: PurchaseVerificationData(
    localVerificationData: 'local-blob',
    serverVerificationData: 'server-blob',
    source: 'fake',
  ),
  transactionDate: status == PurchaseStatus.purchased ? '1' : null,
  status: status,
)..pendingCompletePurchase = true;

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  late FakePlatform platform;

  setUp(() {
    platform = FakePlatform();
    InAppPurchasePlatform.instance = platform;
  });

  tearDown(() {
    InAppPurchasePlatform.instance = FakePlatform();
  });

  test('maps product details to catalog entries', () async {
    platform.queryResponse = ProductDetailsResponse(
      productDetails: [
        ProductDetails(
          id: 'pro',
          title: 'Pro',
          description: 'Lifetime',
          price: r'$1.99',
          rawPrice: 1.99,
          currencyCode: 'USD',
        ),
      ],
      notFoundIDs: const [],
    );
    final adapter = InAppPurchaseAdapter(platform);
    final products = await adapter.products({'pro'});
    expect(products.single.id, 'pro');
    expect(products.single.displayPrice, '\$1.99');
  });

  test('product query error surfaces as store_error', () async {
    platform.queryResponse = ProductDetailsResponse(
      productDetails: const [],
      notFoundIDs: const [],
      error: IAPError(source: 'query', code: 'e', message: 'boom'),
    );
    final adapter = InAppPurchaseAdapter(platform);
    await expectLater(
      adapter.products({'pro'}),
      throwsA(
        isA<DwyBillingException>().having(
          (error) => error.code,
          'code',
          'store_error',
        ),
      ),
    );
  });

  test('buy reports a missing product as product_missing', () async {
    final adapter = InAppPurchaseAdapter(platform);
    await expectLater(
      adapter.buy('ghost'),
      throwsA(
        isA<DwyBillingException>().having(
          (error) => error.code,
          'code',
          'product_missing',
        ),
      ),
    );
  });

  test('buy reports a rejected purchase as purchase_rejected', () async {
    platform.acceptBuy = false;
    platform.queryResponse = ProductDetailsResponse(
      productDetails: [
        ProductDetails(
          id: 'pro',
          title: 'Pro',
          description: '',
          price: '',
          rawPrice: 0,
          currencyCode: 'USD',
        ),
      ],
      notFoundIDs: const [],
    );
    final adapter = InAppPurchaseAdapter(platform);
    await expectLater(
      adapter.buy('pro'),
      throwsA(
        isA<DwyBillingException>().having(
          (error) => error.code,
          'code',
          'purchase_rejected',
        ),
      ),
    );
  });

  test(
    'purchase events map status and cache originals for completion',
    () async {
      final adapter = InAppPurchaseAdapter(platform);
      final delivered = <DwyPurchase>[];
      final done = adapter.updates.listen(delivered.add);
      platform.incoming.add([
        event(
          productId: 'pro',
          status: PurchaseStatus.purchased,
          purchaseId: 't1',
        ),
      ]);
      await Future<void>.delayed(Duration.zero);
      await adapter.complete(delivered.single);
      await Future<void>.delayed(Duration.zero);
      expect(delivered.single.status, DwyPurchaseStatus.purchased);
      expect(delivered.single.purchaseId, 't1');
      expect(delivered.single.verificationData, 'server-blob');
      expect(platform.completeCount, 1);
      // 缓存移除后再次 complete 幂等，不再触发插件。
      await adapter.complete(delivered.single);
      expect(platform.completeCount, 1);
      await done.cancel();
    },
  );

  test('restore collects restored purchases emitted by the stream', () async {
    platform.restoreResults = [
      event(
        productId: 'pro',
        status: PurchaseStatus.restored,
        purchaseId: 't2',
      ),
    ];
    final adapter = InAppPurchaseAdapter(platform);
    final restored = await adapter.restore();
    expect(restored.single.status, DwyPurchaseStatus.restored);
  });
}
