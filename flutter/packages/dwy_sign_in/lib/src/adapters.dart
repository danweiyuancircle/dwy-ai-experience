import 'models.dart';

/// 第三方登录提供商的抽象边界；新增提供商（微信等）时实现本接口。
///
/// 实现约束：
/// - 失败统一抛 [DwySignInException]，用户取消必须是 `user_canceled`，
///   不得把取消伪装成错误或返回空凭据。
/// - 凭据获取后原样返回，不做本地校验、不落盘、不写日志。
abstract class DwySignInAdapter {
  /// 提供商标识，与 [DwySocialIdentity.provider] 一致。
  String get provider;

  /// 拉起该提供商的登录界面并返回凭据；每次调用都是一次完整登录。
  Future<DwySocialIdentity> signIn();

  /// 客户端侧登出（断开与提供商的连接）；后端会话注销由业务方处理。
  Future<void> signOut();
}
