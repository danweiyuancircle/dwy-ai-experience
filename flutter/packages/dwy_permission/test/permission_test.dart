import 'package:dwy_permission/dwy_permission.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';

/// 记录调用并回放预设结果；验证门面契约，不弹系统权限框。
class FakePermissions implements DwyPermissionAdapter {
  DwyPermissionStatus status = DwyPermissionStatus.denied;
  DwyPermissionStatus requestResult = DwyPermissionStatus.granted;
  bool rationale = false;
  bool settingsOpened = false;
  int statusReads = 0;
  int requests = 0;
  Object? failure;

  @override
  Future<DwyPermissionStatus> statusOf(DwyPermissionKind kind) async {
    statusReads += 1;
    final error = failure;
    if (error != null) throw error;
    return status;
  }

  @override
  Future<DwyPermissionStatus> request(DwyPermissionKind kind) async {
    requests += 1;
    final error = failure;
    if (error != null) throw error;
    return requestResult;
  }

  @override
  Future<bool> shouldExplain(DwyPermissionKind kind) async => rationale;

  @override
  Future<bool> openSettings() async => settingsOpened;
}

void main() {
  test('status reads without requesting', () async {
    final adapter = FakePermissions()..status = DwyPermissionStatus.granted;
    final permissions = DwyPermissions.withAdapter(adapter);

    expect(
      await permissions.status(DwyPermissionKind.camera),
      DwyPermissionStatus.granted,
    );
    expect(adapter.statusReads, 1);
    expect(adapter.requests, 0);
  });

  test('denied status does not open a prompt until request', () async {
    final adapter = FakePermissions()
      ..status = DwyPermissionStatus.denied
      ..requestResult = DwyPermissionStatus.granted;
    final permissions = DwyPermissions.withAdapter(adapter);

    expect(
      (await permissions.status(DwyPermissionKind.microphone)).canUse,
      isFalse,
    );
    expect(adapter.requests, 0);

    expect(
      await permissions.request(DwyPermissionKind.microphone),
      DwyPermissionStatus.granted,
    );
    expect(adapter.requests, 1);
  });

  test('permanentlyDenied is only a request result', () async {
    final adapter = FakePermissions()
      ..status = DwyPermissionStatus.denied
      ..requestResult = DwyPermissionStatus.permanentlyDenied;
    final permissions = DwyPermissions.withAdapter(adapter);

    final current = await permissions.status(
      DwyPermissionKind.locationWhenInUse,
    );
    final asked = await permissions.request(
      DwyPermissionKind.locationWhenInUse,
    );

    expect(current.canAskAgain, isTrue);
    expect(asked.canAskAgain, isFalse);
    expect(asked.canUse, isFalse);
  });

  test('limited and provisional access can still be used', () {
    expect(DwyPermissionStatus.limited.canUse, isTrue);
    expect(DwyPermissionStatus.provisional.canUse, isTrue);
    expect(DwyPermissionStatus.restricted.canUse, isFalse);
    expect(DwyPermissionStatus.restricted.canAskAgain, isFalse);
  });

  test('platform failures keep the plugin code', () async {
    final adapter = FakePermissions()
      ..failure = PlatformException(code: 'missing_usage_description');
    final permissions = DwyPermissions.withAdapter(adapter);

    await expectLater(
      permissions.request(DwyPermissionKind.notifications),
      throwsA(
        isA<DwyPermissionException>().having(
          (error) => error.code,
          'code',
          'missing_usage_description',
        ),
      ),
    );
  });

  test('settings open is explicit and does not request', () async {
    final adapter = FakePermissions()..settingsOpened = true;
    final permissions = DwyPermissions.withAdapter(adapter);

    expect(await permissions.openSettings(), isTrue);
    expect(adapter.requests, 0);
  });
}
