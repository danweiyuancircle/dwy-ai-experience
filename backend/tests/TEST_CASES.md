# Backend integration test inventory

Existing package-wide inventory: `../TEST_CASES.md`. Provider-specific inventory: `providers/TEST_CASES.md`.

## Apple transport (`test_auth_apple.py`)

- 挑战与结构化登录保持现有 token/user 信封及 no-store；设备标识只用于会话。
- 绑定需要当前会话与重新认证，拒绝匿名绑定挑战。
- 未知或过大凭据在服务前拒绝，校验响应不回显原始授权材料；账号通知使用独立 payload 协议。

## Email language integration (`test_auth_runtime.py`)

- Optional bounded `Accept-Language`: Chinese and Chinese variants select `zh`; missing/other/excluded ranges select `en`; over 512 characters is rejected before delivery.
- Registration and password-reset HTTP requests pass language through AuthRuntime and EapiEmailCodeSender into the Resend subject, HTML, and text payload; SDK delivery is captured without network calls.
- Changing language cannot bypass the same mailbox/purpose resend cooldown.
