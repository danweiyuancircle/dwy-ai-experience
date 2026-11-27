import 'models.dart';

/// 权限插件的替换缝。测试注入 Fake；生产用插件实现。
///
/// 实现约束：`statusOf` 不弹系统框；`request` 才可能弹框；
/// 失败抛平台异常，由门面收成 [DwyPermissionException]。
abstract interface class DwyPermissionAdapter {
  /// 读当前授权，不向用户展示请求。
  Future<DwyPermissionStatus> statusOf(DwyPermissionKind kind);

  /// 在用户主动操作后请求。已授权时插件不再弹框，直接返回当前状态。
  Future<DwyPermissionStatus> request(DwyPermissionKind kind);

  /// Android：是否应在下一次请求前先解释用途。iOS 固定返回 false。
  Future<bool> shouldExplain(DwyPermissionKind kind);

  /// 打开本应用的系统设置页。返回值只表示系统是否接受了打开请求。
  Future<bool> openSettings();
}
