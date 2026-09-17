# 0.x 内部 breaking

0.x 的 minor 也可以不兼容。整条线仍用 `v0/`，破坏点记在这里。细节 clone `dwyeapi@x.y.z`，不要另开 `v0.10/` 目录。

完整段落以该 tag 的 `backend/CHANGELOG.md` 为准。

| 版本 | 破坏点 |
|------|--------|
| 0.6.0 | 信封改为 `ApiResponse[T]` / `PageData[T]`；删除 `success` / `fail` / `paginated`；`code` 成功态从 int `200` 改为 `"SUCCESS"` |
| 0.9.0 | 删除 `MockEmailProvider`、`AliyunEmailProvider`、整个 `providers.sms`；`EMAIL__PROVIDER` 改为自由字符串；mock/阿里云改业务 `register_email_provider` |
| 0.10.0 | `send_code` 默认校验常见邮箱域名；非白名单抛 `EMAIL_DOMAIN_NOT_ALLOWED`。B2B 设 `EMAIL__REQUIRE_COMMON_DOMAIN=false` |

0.9.6 起新增 `dwyeapi.email` 与 Redis key 规范化，对旧调用方兼容（发码 key 折到同一收件箱）。能力下限见 `email-canonical.md`。

常见域名白名单：`send_code` 默认启用 `require_common_email_domain`（≥0.10.0，`EMAIL__REQUIRE_COMMON_DOMAIN=true`）。B2B 可关。
