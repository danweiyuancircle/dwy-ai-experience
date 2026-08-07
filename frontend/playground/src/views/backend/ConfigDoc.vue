<script setup lang="ts">
import DocPage from '../../components/DocPage.vue'

const content = `
## config — Pydantic Settings

\`\`\`python
from dwyeapi.config import BaseSettings, is_dev, is_prod, get_environment
# 或 from dwyeapi import BaseSettings, is_dev, is_prod, get_environment
\`\`\`

子类化后使用，从 \`.env\` 或环境变量读取配置。嵌套字段用双下划线 \`__\` 分隔。

\`\`\`python
class Settings(BaseSettings):
    app_name: str = "My API"
    # 继承字段见下表
\`\`\`

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| database_url | str | **必填** | 异步数据库 URL |
| redis_url | str | **必填** | Redis URL |
| secret_key | str | **必填** | JWT 签名密钥（建议 ≥32 位） |
| jwt_algorithm | str | \`"HS256"\` | JWT 算法 |
| access_token_expire_minutes | int | \`30\` | Token 过期分钟 |
| environment | \`"dev" \\| "prod"\` | \`"prod"\` | 运行环境，默认 prod（安全默认） |
| allowed_origins | list[str] | \`[]\` | CORS 允许域名，生产禁止 \`['*']\` |
| task_max_jobs | int | \`5\` | ARQ worker 并发上限 |
| task_job_timeout | int | \`3600\` | 单任务超时（秒） |
| task_failure_ttl | int | \`86400\` | 失败任务结果保留（秒） |
| log_level | str | \`"INFO"\` | 最低日志级别 |

> **已移除：** \`debug: bool\`。请用 \`environment\` + \`is_dev()\` / \`is_prod()\`。

### 环境 API

\`\`\`python
from dwyeapi import is_dev, is_prod, get_environment

# FastAPI docs 仅在 dev 暴露
app = FastAPI(
    docs_url="/docs" if is_dev() else None,
    redoc_url="/redoc" if is_dev() else None,
    openapi_url="/openapi.json" if is_dev() else None,
)
\`\`\`

### 典型用法

\`\`\`python
# config.py
from dwyeapi.config import BaseSettings

class Settings(BaseSettings):
    app_name: str = "My API"

settings = Settings()  # 实例化时同步 environment 到模块全局
\`\`\`

> **注意：** \`database_url\`、\`redis_url\`、\`secret_key\` 为必填字段，需在 \`.env\` 或环境变量中提供。
`
</script>

<template>
  <DocPage :content="content" />
</template>
