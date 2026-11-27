/// 跨 iOS / Android 的权限快照。不暴露插件类型，替换底座时只改映射。
library;

/// 应用会向系统申请的权限。
///
/// 不包含存储、短信、电话、安装未知应用。相册读写仍走 [dwy_media]，
/// 这里的 photos 只给不走相册枚举、只要系统授权状态的调用方。
enum DwyPermissionKind {
  camera,
  microphone,
  photos,
  photosAddOnly,
  locationWhenInUse,
  locationAlways,
  notifications,
  contacts,
  calendar,
  reminders,
  bluetooth,
  speech,
  sensors,
}

/// 一次查询或请求的结果。
///
/// Android 13 起 `status` 不再返回 [permanentlyDenied]，该值只出现在
/// `request` 的返回值。调用方不要用状态查询判断「不再询问」。
enum DwyPermissionStatus {
  /// 尚未决定，或用户拒绝但仍可再次请求。
  denied,

  /// 已授权。
  granted,

  /// 系统限制（如家长控制），用户无法在设置里改。仅 iOS。
  restricted,

  /// 部分授权（相册可见子集）。iOS 14+ / Android 14+。
  limited,

  /// 再次请求不会弹窗，只能去系统设置改。
  permanentlyDenied,

  /// 临时授权非打断通知。仅 iOS 12+。
  provisional;

  /// 当前结果能否直接使用对应能力。limited 只覆盖用户选中的子集。
  bool get canUse => this == granted || this == limited || this == provisional;

  /// 再次 request 是否还会弹系统框。restricted 与 permanentlyDenied 不会。
  bool get canAskAgain => this != permanentlyDenied && this != restricted;
}

/// 插件失败。[code] 是插件原始错误码，供调用方分支；不把平台异常类型泄出去。
class DwyPermissionException implements Exception {
  const DwyPermissionException(this.code, {this.cause});

  final String code;
  final Object? cause;

  @override
  String toString() => 'DwyPermissionException($code)';
}
