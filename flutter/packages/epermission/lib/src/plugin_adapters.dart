import 'package:permission_handler/permission_handler.dart';

import 'adapters.dart';
import 'models.dart';

/// `permission_handler` 13.0.2 的 iOS / Android 映射。
///
/// 宿主必须自己声明 Info.plist 用途文案和 Android 权限，并只打开实际使用的
/// iOS 权限宏。本类不改宿主工程。Android `compileSdk` 需 37。
class PermissionHandlerAdapter implements DwyPermissionAdapter {
  const PermissionHandlerAdapter();

  @override
  Future<DwyPermissionStatus> statusOf(DwyPermissionKind kind) async =>
      _status(await _permission(kind).status);

  @override
  Future<DwyPermissionStatus> request(DwyPermissionKind kind) async =>
      _status(await _permission(kind).request());

  @override
  Future<bool> shouldExplain(DwyPermissionKind kind) =>
      _permission(kind).shouldShowRequestRationale;

  @override
  Future<bool> openSettings() => openAppSettings();

  Permission _permission(DwyPermissionKind kind) => switch (kind) {
    DwyPermissionKind.camera => Permission.camera,
    DwyPermissionKind.microphone => Permission.microphone,
    DwyPermissionKind.photos => Permission.photos,
    DwyPermissionKind.photosAddOnly => Permission.photosAddOnly,
    DwyPermissionKind.locationWhenInUse => Permission.locationWhenInUse,
    DwyPermissionKind.locationAlways => Permission.locationAlways,
    DwyPermissionKind.notifications => Permission.notification,
    DwyPermissionKind.contacts => Permission.contacts,
    DwyPermissionKind.calendar => Permission.calendarFullAccess,
    DwyPermissionKind.reminders => Permission.reminders,
    DwyPermissionKind.bluetooth => Permission.bluetooth,
    DwyPermissionKind.speech => Permission.speech,
    DwyPermissionKind.sensors => Permission.sensors,
  };

  DwyPermissionStatus _status(PermissionStatus status) => switch (status) {
    PermissionStatus.denied => DwyPermissionStatus.denied,
    PermissionStatus.granted => DwyPermissionStatus.granted,
    PermissionStatus.restricted => DwyPermissionStatus.restricted,
    PermissionStatus.limited => DwyPermissionStatus.limited,
    PermissionStatus.permanentlyDenied => DwyPermissionStatus.permanentlyDenied,
    PermissionStatus.provisional => DwyPermissionStatus.provisional,
  };
}
