import 'package:dwy_permission/dwy_permission.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:permission_handler_platform_interface/permission_handler_platform_interface.dart';

/// 替换插件平台实现，验证默认门面的状态映射，不触盖真机权限框。
class FakePermissionPlatform extends PermissionHandlerPlatform {
  PermissionStatus next = PermissionStatus.denied;
  Permission? checked;
  Permission? requested;

  @override
  Future<PermissionStatus> checkPermissionStatus(Permission permission) async {
    checked = permission;
    return next;
  }

  @override
  Future<Map<Permission, PermissionStatus>> requestPermissions(
    List<Permission> permissions,
  ) async {
    requested = permissions.single;
    return {permissions.single: next};
  }
}

void main() {
  late FakePermissionPlatform platform;

  setUp(() {
    platform = FakePermissionPlatform();
    PermissionHandlerPlatform.instance = platform;
  });

  test('maps plugin statuses and the camera permission', () async {
    final permissions = DwyPermissions();
    final cases = {
      PermissionStatus.denied: DwyPermissionStatus.denied,
      PermissionStatus.granted: DwyPermissionStatus.granted,
      PermissionStatus.restricted: DwyPermissionStatus.restricted,
      PermissionStatus.limited: DwyPermissionStatus.limited,
      PermissionStatus.permanentlyDenied: DwyPermissionStatus.permanentlyDenied,
      PermissionStatus.provisional: DwyPermissionStatus.provisional,
    };

    for (final entry in cases.entries) {
      platform.next = entry.key;
      expect(await permissions.status(DwyPermissionKind.camera), entry.value);
    }
    expect(platform.checked, Permission.camera);
    expect(platform.requested, isNull);
  });

  test('request uses the plugin request and does not check first', () async {
    platform.next = PermissionStatus.granted;
    final permissions = DwyPermissions();

    expect(
      await permissions.request(DwyPermissionKind.notifications),
      DwyPermissionStatus.granted,
    );
    expect(platform.requested, Permission.notification);
    expect(platform.checked, isNull);
  });
}
