<script setup lang="ts">
import DocPage from '../../components/DocPage.vue'

const content = `
## security — JWT + bcrypt

\`\`\`python
from danweiyuan_base.security import hash_password, verify_password, create_token, decode_token
\`\`\`

所有函数无状态，密钥通过参数传入。

| 函数 | 签名 | 说明 |
|------|------|------|
| hash_password | \`(password: str) -> str\` | bcrypt 哈希 |
| verify_password | \`(plain: str, hashed: str) -> bool\` | 验证密码 |
| create_token | \`(data: dict, secret: str, expires_minutes: int, algorithm="HS256") -> str\` | 创建 JWT，自动添加 exp |
| decode_token | \`(token: str, secret: str, algorithm="HS256") -> dict \\| None\` | 解码 JWT，失败返回 None |

### 使用示例

\`\`\`python
hashed = hash_password("my-password")
is_valid = verify_password("my-password", hashed)

token = create_token({"sub": str(user.id)}, settings.secret_key, settings.access_token_expire_minutes)
payload = decode_token(token, settings.secret_key)  # {"sub": "1", "exp": ...} 或 None
\`\`\`

### 设计要点

- **无状态设计：** 所有函数不依赖全局变量，密钥和配置通过参数传入
- **bcrypt 哈希：** \`hash_password\` 使用 bcrypt 算法，自动生成 salt
- **JWT 自动过期：** \`create_token\` 自动在 payload 中添加 \`exp\` 字段
- **安全解码：** \`decode_token\` 验证失败（过期、签名错误等）统一返回 \`None\`，不抛异常
`
</script>

<template>
  <DocPage :content="content" />
</template>
