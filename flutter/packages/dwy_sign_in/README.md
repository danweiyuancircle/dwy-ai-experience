# dwy_sign_in

提供商无关的第三方登录基础库：业务面对统一的 `DwySignInAdapter` 接口与
`DwySocialIdentity` 凭据模型，当前内置 Apple（`sign_in_with_apple`）与
Google（`google_sign_in`）实现；新增提供商（微信等）时实现一个 adapter 即可。

## 边界

- 只负责客户端凭据获取：`identityToken`（Apple identityToken / Google
  idToken）**必须**由业务后端向平台验证后换发自家会话；本库不连后端、
  不校验、不落盘、不打日志。
- Apple 的 `authorizationCode` 一并透传，供后端调用撤销接口
  （App Store 审核对提供第三方登录的 App 硬性要求可撤销）。
- 姓名/邮箱仅在用户**首次**授权时返回（Apple 尤其严格），之后为 null，
  业务层不得视为失败。
- 不定义登录按钮 UI；`sign_in_with_apple` 自带按钮组件可由业务直接使用。

## 用法

```dart
final apple = AppleSignIn();          // 或 GoogleSignInProvider()
try {
  final identity = await apple.signIn();
  // 把 identity.identityToken（及 Apple 的 authorizationCode）POST 给
  // 业务后端 /auth/apple 等端点，换发自家会话后再更新 UI。
} on DwySignInException catch (error) {
  // code: user_canceled / unavailable / provider_error
}
await apple.signOut(); // 客户端侧登出；后端会话注销由业务调用自家接口
```

Google 需要业务 App 先完成平台配置（iOS URL Scheme、Android
`serverClientId`），`GoogleSignInProvider.initialize` 由库内首次登录时调用。

## 测试

```sh
flutter test
```

平台交互通过 platform interface Fake 覆盖；真机商店弹窗、真实凭据签发
由业务 App 真机验收，不在本包测试范围。
