<script setup lang="ts">
import DocPage from '../../components/DocPage.vue'

const content = `
## config — Pydantic Settings

\`\`\`python
from danweiyuan_eapi.config import BaseSettings
\`\`\`

子类化后使用，从 \`.env\` 或环境变量读取配置。

\`\`\`python
class Settings(BaseSettings):
    app_name: str = "My API"
    # 继承的必填字段：database_url, redis_url, secret_key
\`\`\`

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| database_url | str | **必填** | 异步数据库 URL |
| redis_url | str | **必填** | Redis URL |
| secret_key | str | **必填** | JWT 签名密钥 |
| jwt_algorithm | str | \`"HS256"\` | JWT 算法 |
| access_token_expire_minutes | int | \`30\` | Token 过期分钟 |
| debug | bool | \`False\` | 调试模式 |
| allowed_origins | list[str] | \`[]\` | CORS 允许域名 |

### 典型用法

\`\`\`python
# config.py
from danweiyuan_eapi.config import BaseSettings

class Settings(BaseSettings):
    app_name: str = "My API"

settings = Settings()
\`\`\`

> **注意：** \`database_url\`、\`redis_url\`、\`secret_key\` 为必填字段，需在 \`.env\` 文件或环境变量中提供。
`
</script>

<template>
  <DocPage :content="content" />
</template>
