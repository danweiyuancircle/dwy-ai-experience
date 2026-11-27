import 'package:dwy_sign_in/dwy_sign_in.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:google_sign_in_platform_interface/google_sign_in_platform_interface.dart';

/// 记录调用并回放预设登录结果的 Fake 平台。
class FakeGooglePlatform extends GoogleSignInPlatform {
  GoogleSignInUserData? user;
  String? idToken = 'google-jwt';
  GoogleSignInException? failure;
  int signOutCount = 0;

  @override
  Future<void> init(InitParameters params) async {}

  @override
  Future<AuthenticationResults> authenticate(
    AuthenticateParameters params,
  ) async {
    final failure = this.failure;
    if (failure != null) throw failure;
    return AuthenticationResults(
      user: user!,
      authenticationTokens: AuthenticationTokenData(idToken: idToken),
    );
  }

  @override
  Future<void> signOut(SignOutParams params) async => signOutCount++;

  @override
  Future<void> disconnect(DisconnectParams params) async {}

  @override
  bool supportsAuthenticate() => true;

  @override
  bool authorizationRequiresUserInteraction() => false;

  @override
  Future<ClientAuthorizationTokenData?> clientAuthorizationTokensForScopes(
    ClientAuthorizationTokensForScopesParameters params,
  ) async => null;

  @override
  Future<ServerAuthorizationTokenData?> serverAuthorizationTokensForScopes(
    ServerAuthorizationTokensForScopesParameters params,
  ) async => null;

  @override
  Future<AuthenticationResults?> attemptLightweightAuthentication(
    AttemptLightweightAuthenticationParameters params,
  ) async => null;
}

GoogleSignInUserData user({String? displayName}) => const GoogleSignInUserData(
  email: 'jdoe@example.org',
  id: 'google-user-1',
  displayName: 'John Doe',
);

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  late FakeGooglePlatform platform;

  setUp(() {
    platform = FakeGooglePlatform();
    GoogleSignInPlatform.instance = platform;
  });

  tearDown(() {
    GoogleSignInPlatform.instance = FakeGooglePlatform();
  });

  test('maps Google credentials from an authenticated account', () async {
    platform.user = user();
    final provider = GoogleSignInProvider();
    final identity = await provider.signIn();
    expect(identity.provider, 'google');
    expect(identity.identityToken, 'google-jwt');
    expect(identity.userHint, 'google-user-1');
    expect(identity.displayName, 'John Doe');
    expect(identity.email, 'jdoe@example.org');
    // 登出转发给平台层。
    await provider.signOut();
    expect(platform.signOutCount, 1);
  });

  test('reports user cancel as user_canceled', () async {
    platform.user = user();
    platform.failure = const GoogleSignInException(
      code: GoogleSignInExceptionCode.canceled,
      description: 'canceled',
    );
    await expectLater(
      GoogleSignInProvider().signIn(),
      throwsA(
        isA<DwySignInException>().having(
          (error) => error.code,
          'code',
          'user_canceled',
        ),
      ),
    );
  });

  test('rejects a missing id token as provider_error', () async {
    platform.user = user();
    platform.idToken = null;
    await expectLater(
      GoogleSignInProvider().signIn(),
      throwsA(
        isA<DwySignInException>().having(
          (error) => error.code,
          'code',
          'provider_error',
        ),
      ),
    );
  });

  test('reports platform failures as provider_error', () async {
    platform.user = user();
    platform.failure = const GoogleSignInException(
      code: GoogleSignInExceptionCode.unknownError,
      description: 'offline',
    );
    await expectLater(
      GoogleSignInProvider().signIn(),
      throwsA(
        isA<DwySignInException>().having(
          (error) => error.code,
          'code',
          'provider_error',
        ),
      ),
    );
  });
}
