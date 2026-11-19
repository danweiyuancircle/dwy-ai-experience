import 'package:sign_in_with_apple/sign_in_with_apple.dart';

import 'adapters.dart';
import 'models.dart';

/// 基于 `sign_in_with_apple` 的 Apple 登录实现。
///
/// Apple 只在**首次**授权返回姓名与邮箱，之后登录这些字段为 null，
/// 这是平台行为，业务层不得视为失败。
class AppleSignIn implements DwySignInAdapter {
  const AppleSignIn();

  @override
  String get provider => 'apple';

  @override
  Future<DwySocialIdentity> signIn() async {
    try {
      // 姓名与邮箱必须显式请求；用户可拒绝单项授权。
      final credential = await SignInWithApple.getAppleIDCredential(
        scopes: [
          AppleIDAuthorizationScopes.fullName,
          AppleIDAuthorizationScopes.email,
        ],
      );
      final token = credential.identityToken;
      if (token == null || token.isEmpty) {
        throw const DwySignInException('provider_error', 'Apple 未返回身份凭据');
      }
      return DwySocialIdentity(
        provider: provider,
        identityToken: token,
        // 授权码交后端用于撤销授权；撤销入口是 App Store 审核硬性要求。
        authorizationCode: credential.authorizationCode,
        userHint: credential.userIdentifier,
        displayName: joinDisplayName(
          credential.givenName,
          credential.familyName,
        ),
        email: credential.email,
      );
    } on SignInWithAppleAuthorizationException catch (error) {
      if (error.code == AuthorizationErrorCode.canceled) {
        throw const DwySignInException('user_canceled', '已取消登录');
      }
      throw DwySignInException('provider_error', error.message);
    } on SignInWithAppleNotSupportedException {
      throw const DwySignInException('unavailable', '当前设备不支持 Apple 登录');
    }
  }

  @override
  Future<void> signOut() async {
    // Apple 登录没有客户端「登出」；撤销授权须由后端凭授权码调用 Apple
    // revocation 接口，客户端侧无事可做。
  }
}

/// 合并姓名为单个显示名；两段任一为空时跳过，全空返回 null。
String? joinDisplayName(String? givenName, String? familyName) {
  final parts = [
    givenName,
    familyName,
  ].nonNulls.where((part) => part.isNotEmpty).toList();
  return parts.isEmpty ? null : parts.join(' ');
}
