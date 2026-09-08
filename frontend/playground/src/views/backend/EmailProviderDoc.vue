<script setup lang="ts">
import DocPage from '../../components/DocPage.vue'

const content = `
## email — 邮箱规范化 + 邮件验证码 Provider

### 邮箱规范化（Gmail 别名）

Gmail 把 plus、点号、\`googlemail.com\` 当成同一收件箱。注册查重、登录查找、用户表写入必须走规范化结果，否则同一邮箱可开多个号。

\`\`\`python
from dwyeapi.email import canonicalize_email, is_folded_alias, GMAIL_DOMAINS

canonicalize_email("Bai.Wen+1@Gmail.com")   # baiwen@gmail.com
canonicalize_email("a.b@googlemail.com")    # ab@gmail.com
canonicalize_email("Alfred+ops@icloud.com") # alfred+ops@icloud.com（其它域名只 lower）
is_folded_alias("a+x@gmail.com")            # True
is_folded_alias("A@gmail.com")              # False（仅大小写不算折叠）
\`\`\`

- 其它域名只做 strip + lower，保留 \`+\` 与点
- \`send_code\` / \`verify_code\` 的 Redis key **已自动规范化**；发信信封仍用用户输入的地址
- 业务层存库、唯一性检查仍要自己调 \`canonicalize_email\`

## email — 邮件验证码 Provider

\`\`\`python
pip install "dwyeapi[email]"  # 或 email-resend

from dwyeapi.providers.email import (
    EmailSettings,
    make_email_provider,
    register_email_provider,
    EmailProviderBase,
)
\`\`\`

### 内置 resend

环境变量（嵌套 \`__\`）：

| 变量 | 说明 |
|------|------|
| EMAIL__PROVIDER | 默认 \`resend\` |
| EMAIL__RESEND__API_KEY | **必填** |
| EMAIL__RESEND__FROM_EMAIL | **必填**（工厂校验） |
| EMAIL__CODE_TTL | 验证码 TTL 秒，默认 300 |
| EMAIL__CODE_LENGTH | 位数，默认 6 |
| EMAIL__BRAND_* | 品牌化模板字段 |

\`\`\`python
provider = make_email_provider(settings.email)
ok = await provider.send_code("user@example.com")
valid = await provider.verify_code("user@example.com", code)
\`\`\`

### 行为约束

- **先发送后写 Redis**：\`_send\` 失败不落库，避免未收到邮件却有可校验码
- **校验成功删除 key**（一次性）；错误码保留 key（可重试）
- 工厂缺少 \`api_key\` / \`from_email\` 直接 \`ValueError\`

### 注册表

内置与自定义走同一张表。`make_email_provider` 只按 `EMAIL__PROVIDER` 查名，业务 `register_email_provider` 后即可切换，不用改 eapi。内置名 `resend` 不可覆盖。

### 自定义 Provider

\`\`\`python
class MyProvider(EmailProviderBase):
    async def _send(self, target: str, code: str) -> bool:
        # 调用自家 SMTP / 厂商 SDK
        return True

register_email_provider("my_smtp", lambda s: MyProvider(code_ttl=s.code_ttl))
# .env: EMAIL__PROVIDER=my_smtp
\`\`\`

### 安全建议（业务层）

- 发送频控、试错次数上限（基类未内置）
- 生产勿公网裸奔验证码接口
`
</script>

<template>
  <DocPage :content="content" />
</template>
