import 'package:dwy_sign_in/dwy_sign_in.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sign_in_with_apple_platform_interface/sign_in_with_apple_platform_interface.dart';

/// 记录请求并回放预设授权结果的 Fake 平台。
class FakeApplePlatform extends SignInWithApplePlatform {
  AuthorizationCredentialAppleID? credential;
  SignInWithAppleAuthorizationException? failure;

  @override
  Future<bool> isAvailable() async => true;

  @override
  @override
  Future<AuthorizationCredentialAppleID> getAppleIDCredential({
    required List<AppleIDAuthorizationScopes> scopes,
    WebAuthenticationOptions? webAuthenticationOptions,
    String? nonce,
    String? state,
  }) async {
    final failure = this.failure;
    if (failure != null) throw failure;
    return credential!;
  }
}

AuthorizationCredentialAppleID credential({
  String? givenName,
  String? familyName,
  String? identityToken = 'apple-jwt',
}) => AuthorizationCredentialAppleID(
  userIdentifier: 'apple-user-1',
  givenName: givenName,
  familyName: familyName,
  authorizationCode: 'apple-code',
  email: 'hide@privaterelay.appleid.com',
  identityToken: identityToken,
  state: null,
);

void main() {
  late FakeApplePlatform platform;

  setUp(() {
    platform = FakeApplePlatform();
    SignInWithApplePlatform.instance = platform;
  });

  tearDown(() {
    SignInWithApplePlatform.instance = FakeApplePlatform();
  });

  test('maps Apple credentials with joined display name', () async {
    platform.credential = credential(givenName: 'San', familyName: 'Zhang');
    final identity = await const AppleSignIn().signIn();
    expect(identity.provider, 'apple');
    expect(identity.identityToken, 'apple-jwt');
    expect(identity.authorizationCode, 'apple-code');
    expect(identity.userHint, 'apple-user-1');
    expect(identity.displayName, 'San Zhang');
    expect(identity.email, 'hide@privaterelay.appleid.com');
  });

  test('keeps Apple name parts independent when only one is granted', () async {
    platform.credential = credential(givenName: 'San', familyName: null);
    final identity = await const AppleSignIn().signIn();
    expect(identity.displayName, 'San');
  });

  test('reports user cancel as user_canceled', () async {
    platform.failure = const SignInWithAppleAuthorizationException(
      code: AuthorizationErrorCode.canceled,
      message: 'User canceled authorization',
    );
    await expectLater(
      const AppleSignIn().signIn(),
      throwsA(
        isA<DwySignInException>().having(
          (error) => error.code,
          'code',
          'user_canceled',
        ),
      ),
    );
  });

  test('reports other authorization failures as provider_error', () async {
    platform.failure = const SignInWithAppleAuthorizationException(
      code: AuthorizationErrorCode.invalidResponse,
      message: 'bad response',
    );
    await expectLater(
      const AppleSignIn().signIn(),
      throwsA(
        isA<DwySignInException>().having(
          (error) => error.code,
          'code',
          'provider_error',
        ),
      ),
    );
  });

  test('rejects empty identity tokens', () async {
    platform.credential = credential(identityToken: '');
    await expectLater(
      const AppleSignIn().signIn(),
      throwsA(
        isA<DwySignInException>().having(
          (error) => error.code,
          'code',
          'provider_error',
        ),
      ),
    );
  });

  test('joins display name parts with blanks ignored', () {
    expect(joinDisplayName('San', 'Zhang'), 'San Zhang');
    expect(joinDisplayName(null, 'Zhang'), 'Zhang');
    expect(joinDisplayName('San', ''), 'San');
    expect(joinDisplayName(null, null), isNull);
  });
}
