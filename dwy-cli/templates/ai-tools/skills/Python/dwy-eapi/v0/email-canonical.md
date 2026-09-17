# 邮箱规范化与常见域名白名单（≥0.9.6）

安装版本 `< 0.9.6`：没有 `dwyeapi.email`，不要 import。

```python
from dwyeapi.email import canonicalize_email, is_folded_alias, GMAIL_DOMAINS

canonicalize_email("Bai.Wen+1@Gmail.com")  # baiwen@gmail.com
canonicalize_email("a.b@googlemail.com")   # ab@gmail.com
canonicalize_email("a+x@icloud.com")       # a+x@icloud.com
is_folded_alias("a+x@gmail.com")           # True
is_folded_alias("A@gmail.com")           # False
```

- 注册查重、登录查找、用户表写入 **必须** 走 `canonicalize_email`
- Gmail 把 plus / 点号 / `googlemail.com` 当成同一收件箱，不折会开多个号、绕过发码冷却
- 其它域名只做 strip + lower，保留 `+` 与点
- `send_code` / `verify_code` 的 Redis key 已自动规范化；发信信封仍用用户输入地址

## 常见域名白名单（≥0.10.0）

安装版本 `< 0.10.0`：没有 `is_common_email_domain`，不要 import。一次性邮箱会换马甲域，黑名单跟不上。

**`send_code` 默认校验**（`EMAIL__REQUIRE_COMMON_DOMAIN=true`）。不在白名单：抛 `BusinessError(code="EMAIL_DOMAIN_NOT_ALLOWED")`，不发信、不写 Redis。B2B 可关。

```python
from dwyeapi.email import require_common_email_domain
from dwyeapi.providers.email import EmailSettings

# 发码已默认走白名单；业务也可在注册/换绑再调一次
email = require_common_email_domain(raw)

# .env
# EMAIL__REQUIRE_COMMON_DOMAIN=true
# EMAIL__EXTRA_ALLOW_DOMAINS=yanbofund.com,contek.io
# EMAIL__ALLOW_EDU_CN=true
```

- 精确匹配 `COMMON_EMAIL_DOMAINS`（qq / 163 / gmail / outlook / icloud / proton 等），`mail.qq.com` 不等于 `qq.com`
- 默认放行 `edu.cn` / `*.edu.cn`，不放行任意 `.edu`
- 机构域用 `extra_allow` / `EMAIL__EXTRA_ALLOW_DOMAINS`，不要把公司域写进框架常量表
- 自定义 provider 的 factory 必须把 `require_common_domain` / `extra_allow_domain_list()` / `allow_edu_cn` 传给 `EmailProviderBase`
