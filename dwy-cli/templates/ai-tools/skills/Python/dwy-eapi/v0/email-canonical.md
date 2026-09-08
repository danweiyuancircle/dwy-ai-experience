# 邮箱规范化（≥0.9.6）

安装版本 `< 0.9.6`：没有 `dwyeapi.email`，不要 import。

```python
from dwyeapi.email import canonicalize_email, is_folded_alias, GMAIL_DOMAINS

canonicalize_email("Bai.Wen+1@Gmail.com")  # baiwen@gmail.com
canonicalize_email("a.b@googlemail.com")   # ab@gmail.com
canonicalize_email("a+x@icloud.com")       # a+x@icloud.com
is_folded_alias("a+x@gmail.com")           # True
is_folded_alias("A@gmail.com")             # False
```

- 注册查重、登录查找、用户表写入 **必须** 走 `canonicalize_email`
- Gmail 把 plus / 点号 / `googlemail.com` 当成同一收件箱，不折会开多个号、绕过发码冷却
- 其它域名只做 strip + lower，保留 `+` 与点
- `send_code` / `verify_code` 的 Redis key 已自动规范化；业务存库仍要自己调
