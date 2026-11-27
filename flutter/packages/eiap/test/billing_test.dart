import 'dart:async';

import 'package:dwy_iap/dwy_iap.dart';
import 'package:flutter_test/flutter_test.dart';

/// 记录调用并回放预设结果的 Fake 商店；验证门面契约，不依赖平台插件。
class FakeBilling implements DwyBillingAdapter {
  FakeBilling();

  List<DwyProduct> catalog = const [];
  bool isAvailable = true;
  Exception? Function()? onBuy;
  List<DwyPurchase> restored = [];
  final StreamController<DwyPurchase> incoming =
      StreamController<DwyPurchase>();
  final List<String> completedIds = [];

  @override
  Future<bool> available() async => isAvailable;

  @override
  Future<List<DwyProduct>> products(Set<String> ids) async =>
      catalog.where((product) => ids.contains(product.id)).toList();

  @override
  Future<void> buy(String productId) async {
    final failure = onBuy;
    if (failure != null) throw failure()!;
  }

  @override
  Future<List<DwyPurchase>> restore() async => restored;

  @override
  Stream<DwyPurchase> get updates => incoming.stream;

  @override
  Future<void> complete(DwyPurchase purchase) async =>
      completedIds.add(purchase.productId);
}

DwyProduct product(String id) => DwyProduct(
  id: id,
  title: 'title-$id',
  description: 'desc-$id',
  displayPrice: '\$1.99',
);

void main() {
  test('queries only products present in the store catalog', () async {
    final billing = DwyBilling.withAdapter(
      FakeBilling()..catalog = [product('pro'), product('family')],
    );
    final found = await billing.products({'pro', 'ghost'});
    expect(found.map((item) => item.id), ['pro']);
  });

  test('buy forwards to adapter and results arrive via updates', () async {
    final fake = FakeBilling();
    final billing = DwyBilling.withAdapter(fake);
    final delivered = <DwyPurchase>[];
    final done = billing.updates.listen(delivered.add);
    await billing.buy('pro');
    fake.incoming.add(
      const DwyPurchase(
        productId: 'pro',
        status: DwyPurchaseStatus.purchased,
        purchaseId: 'txn-1',
        verificationData: 'jws-payload',
      ),
    );
    await fake.incoming.close();
    await done.cancel();
    expect(delivered.single.status, DwyPurchaseStatus.purchased);
    expect(delivered.single.verificationData, 'jws-payload');
  });

  test('restore returns restored purchases collected by the adapter', () async {
    final fake = FakeBilling()
      ..restored = const [
        DwyPurchase(
          productId: 'pro',
          status: DwyPurchaseStatus.restored,
          verificationData: 'receipt',
        ),
      ];
    final billing = DwyBilling.withAdapter(fake);
    final restored = await billing.restore();
    expect(restored.single.status, DwyPurchaseStatus.restored);
  });

  test('complete forwards purchases to the adapter', () async {
    final fake = FakeBilling();
    final billing = DwyBilling.withAdapter(fake);
    const purchase = DwyPurchase(
      productId: 'pro',
      status: DwyPurchaseStatus.purchased,
    );
    await billing.complete(purchase);
    expect(fake.completedIds, ['pro']);
  });

  test('wraps unexpected platform failures as store_error', () async {
    final fake = FakeBilling()..onBuy = constFormatException;
    final billing = DwyBilling.withAdapter(fake);
    await expectLater(
      billing.buy('pro'),
      throwsA(
        isA<DwyBillingException>().having(
          (error) => error.code,
          'code',
          'store_error',
        ),
      ),
    );
  });

  test('keeps DwyBillingException untouched', () async {
    final fake = FakeBilling()
      ..onBuy = () => const DwyBillingException('purchase_rejected', 'denied');
    final billing = DwyBilling.withAdapter(fake);
    await expectLater(
      billing.buy('pro'),
      throwsA(
        isA<DwyBillingException>().having(
          (error) => error.code,
          'code',
          'purchase_rejected',
        ),
      ),
    );
  });

  test('available reflects the store availability', () async {
    final fake = FakeBilling()..isAvailable = false;
    final billing = DwyBilling.withAdapter(fake);
    expect(await billing.available(), isFalse);
  });
}

/// 制造非本库异常，验证门面的统一包装分支。
Exception constFormatException() => const FormatException('bad store payload');
