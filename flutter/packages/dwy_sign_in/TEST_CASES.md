# dwy_sign_in 测试用例

对应 `test/apple_test.dart` 与 `test/google_test.dart`，均通过 platform
interface Fake 验证；真机弹窗、真实凭据签发由业务 App 真机验收覆盖。

## Apple（apple_test.dart）

| 用例 | 验证点 |
| --- | --- |
| maps Apple credentials with joined display name | 凭据字段完整映射，姓名两段合并 |
| keeps Apple name parts independent when only one is granted | 用户只授权单段姓名时正确保留 |
| reports user cancel as user_canceled | 平台取消映射为固定错误码 |
| reports other authorization failures as provider_error | 其余授权失败折叠为 `provider_error` |
| rejects empty identity tokens | 空 identityToken 不透传 |
| joins display name parts with blanks ignored | `joinDisplayName` 纯函数边界（null/空串） |

## Google（google_test.dart）

| 用例 | 验证点 |
| --- | --- |
| maps Google credentials from an authenticated account | 凭据映射、idToken 透传、signOut 转发 |
| reports user cancel as user_canceled | 平台取消映射为固定错误码 |
| rejects a missing id token as provider_error | 缺 idToken 不透传 |
| reports platform failures as provider_error | 其余平台失败折叠为 `provider_error` |
