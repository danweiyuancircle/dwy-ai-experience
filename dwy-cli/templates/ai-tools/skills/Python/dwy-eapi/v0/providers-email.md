# 邮件 Provider（0.x）

内置与自定义走同一注册表。`make_email_provider` 只按 `EMAIL__PROVIDER` 查名。

当前内置仅 `resend`，extra：`dwyeapi[email-resend]`。`dwyeapi[email]` = 全部内置 extra（现在就这一个）。

```python
from dwyeapi.providers.email import (
    EmailProviderBase,
    EmailSettings,
    make_email_provider,
    register_email_provider,
)

provider = make_email_provider(settings.email)
await provider.send_code("user@qq.com")
```

自定义（**不用改 eapi**）：

```python
class TencentSesProvider(EmailProviderBase):
    async def _send(self, target: str, code: str) -> bool:
        html = self._render_code_html(code)
        text = self._render_code_text(code)
        return True

register_email_provider(
    "tencent_ses",
    lambda s: TencentSesProvider(
        code_ttl=s.code_ttl,
        require_common_domain=s.require_common_domain,
        extra_allow_domains=s.extra_allow_domain_list(),
        allow_edu_cn=s.allow_edu_cn,
    ),
)
# .env: EMAIL__PROVIDER=tencent_ses
```

- 验证码 Redis + 品牌化模板由基类复用，子类只实现 `_send`
- 内置名 `resend` 不可覆盖
- 自定义同名二次注册会覆盖并 warning
- 必须在 `make_email_provider` **之前** register
- `send_code` / `verify_code` 的 Redis key 自 **0.9.6** 走 `canonicalize_email`；发信信封仍用用户输入地址
- `send_code` **默认**校验常见邮箱域名（`EMAIL__REQUIRE_COMMON_DOMAIN`，≥0.10.0）；失败不发信。详见 `email-canonical.md`
- 缺 extra 构造内置 provider → `ImportError`，提示 `pip install dwyeapi[email-resend]`

0.9.0 删除了内置 mock / 阿里云占位 / 整个 sms 模块，见 `breaking.md`。
