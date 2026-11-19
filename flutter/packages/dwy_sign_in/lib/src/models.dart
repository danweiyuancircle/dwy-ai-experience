/// 跨提供商统一的登录结果模型与错误。
///
/// 凭据只做客户端获取与透传：`identityToken` 是平台签发的 JWT，**必须**
/// 交业务后端向平台验证并换发自家会话；本库不调用后端、不保存凭据。
library;

/// 一次第三方登录拿到的身份凭据。
///
/// 平台只在**首次授权**返回姓名邮箱（Apple 尤其严格，仅首次），
/// 之后登录这些字段为 null；业务端不能把「没有姓名」当作失败。
class DwySocialIdentity {
  const DwySocialIdentity({
    required this.provider,
    required this.identityToken,
    this.authorizationCode,
    this.userHint,
    this.displayName,
    this.email,
  });

  /// 提供商标识：`apple` / `google`；新实现沿用小写平台名。
  final String provider;

  /// 平台签发的身份 JWT（Apple identityToken / Google idToken）。
  final String identityToken;

  /// Apple 专用授权码，后端用于撤销授权（App Store 审核要求提供撤销路径）。
  final String? authorizationCode;

  /// 平台侧用户标识（Google 用户 id / Apple user），仅供关联展示。
  final String? userHint;

  /// 平台返回的显示名，可能为 null（未授权或非首次登录）。
  final String? displayName;

  /// 平台返回的邮箱，可能为 null（用户选择隐藏邮箱时是中转地址）。
  final String? email;
}

/// 登录流程中本库定义的失败；未知平台错误统一折叠为 `provider_error`。
class DwySignInException implements Exception {
  const DwySignInException(this.code, this.message);

  /// 固定取值：`user_canceled`、`unavailable`、`provider_error`。
  /// 业务层按 code 分支，不解析 message。
  final String code;
  final String message;

  @override
  String toString() => 'DwySignInException($code, $message)';
}
