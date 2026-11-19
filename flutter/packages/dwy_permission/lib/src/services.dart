import 'package:flutter/services.dart';

import 'adapters.dart';
import 'models.dart';
import 'plugin_adapters.dart';

/// 无界面的权限门面。只在调用方明确调用 [request] 时才可能弹系统框。
///
/// 默认走 [PermissionHandlerAdapter]（`permission_handler` 13.0.2）。
/// 测试用 [DwyPermissions.withAdapter] 注入 Fake，不触盖平台插件。
class DwyPermissions {
  DwyPermissions() : _adapter = const PermissionHandlerAdapter();

  DwyPermissions.withAdapter(this._adapter);

  final DwyPermissionAdapter _adapter;

  /// 读当前状态，不弹请求框。
  Future<DwyPermissionStatus> status(DwyPermissionKind kind) =>
      _guard(() => _adapter.statusOf(kind));

  /// 由用户操作触发的请求。启动时不要调。
  Future<DwyPermissionStatus> request(DwyPermissionKind kind) =>
      _guard(() => _adapter.request(kind));

  /// Android 是否应先展示用途说明。说明文案由业务层决定，本库不弹窗。
  Future<bool> shouldExplain(DwyPermissionKind kind) =>
      _guard(() => _adapter.shouldExplain(kind));

  /// 打开系统设置。返回后要再调 [status]，不要假设用户已经改授权。
  Future<bool> openSettings() => _guard(_adapter.openSettings);

  Future<T> _guard<T>(Future<T> Function() action) async {
    try {
      return await action();
    } on PlatformException catch (error) {
      throw DwyPermissionException(error.code, cause: error);
    }
  }
}
