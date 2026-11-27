import 'package:google_sign_in/google_sign_in.dart';

import 'adapters.dart';
import 'models.dart';

/// 基于 Flutter 官方 `google_sign_in` 7.x 的 Google 登录实现。
///
/// `initialize` 的 client 配置（serverClientId 等）由业务 App 按平台
/// 传入；idToken 需要配置 serverClientId 后才会签发。
class GoogleSignInProvider implements DwySignInAdapter {
  GoogleSignInProvider({GoogleSignIn? signIn})
    : _signIn = signIn ?? GoogleSignIn.instance;

  final GoogleSignIn _signIn;
  bool _initialized = false;

  @override
  String get provider => 'google';

  @override
  Future<DwySocialIdentity> signIn() async {
    // 7.x 要求先 initialize；重复调用同一单例会抛错，这里保证只初始化一次。
    if (!_initialized) {
      await _signIn.initialize();
      _initialized = true;
    }
    try {
      final account = await _signIn.authenticate();
      final idToken = account.authentication.idToken;
      if (idToken == null || idToken.isEmpty) {
        throw const DwySignInException('provider_error', 'Google 未返回身份凭据');
      }
      return DwySocialIdentity(
        provider: provider,
        identityToken: idToken,
        userHint: account.id,
        displayName: account.displayName,
        // email 恒为非空串；用户可能授权受限账号，空串按无邮箱处理。
        email: account.email.isEmpty ? null : account.email,
      );
    } on GoogleSignInException catch (error) {
      if (error.code == GoogleSignInExceptionCode.canceled) {
        throw const DwySignInException('user_canceled', '已取消登录');
      }
      throw DwySignInException('provider_error', error.description ?? '登录失败');
    }
  }

  @override
  Future<void> signOut() => _signIn.signOut();
}
