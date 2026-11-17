# AuthUI

- 邮箱格式错误时阻止提交。
- 注册后返回已认证用户并清除页面密码、验证码。
- 账号已创建但会话保存失败时返回登录页，提示不要重复注册。
- 更改邮箱后原 challenge 失效。
- 注册密码长度、UTF-8 字节数边界。
- 重置成功返回登录页，不自动建立新会话。
- 重发倒计时、验证码到期使用可控时间。
- 取消后迟到请求不能触发登录完成。
- 未知服务端错误不显示原始信息。
- 中文英文组件文案资源。

## 双端统一第三方登录增量（2026-10-28）

- `testCancelledExternalAuthorizationNeverInvokesSignIn`：Apple原生授权迟到回调在取消后不能启动业务登录。
- `testExternalSignInClearsSecretsAndMapsPurchaseConflict`：第三方成功清理秘密；购买归属冲突仅显示安全固定文案。
