<script setup lang="ts">
import DocPage from '../../components/DocPage.vue'

const content = `
## health — 健康检查

\`\`\`python
from dwyeapi import health
# health.create_health_router(...)
\`\`\`

**只探活（liveness）**，不连接 PostgreSQL / Redis。健康端点常对公网开放，内置依赖探测会被当成 DoS 放大器。

### 用法

\`\`\`python
from dwyeapi import health

app.include_router(
    health.create_health_router(
        service_name="my-api",
        version="1.0.0",
        path="/health",
    )
)
\`\`\`

### 响应示例

\`\`\`json
{
  "code": "SUCCESS",
  "message": "success",
  "data": {
    "service": "my-api",
    "version": "1.0.0",
    "status": "alive"
  },
  "timestamp": 1711872000
}
\`\`\`

### 参数

| 参数 | 默认 | 说明 |
|------|------|------|
| service_name | 必填 | 服务名 |
| version | 必填 | 版本号 |
| path | \`"/health"\` | 端点路径 |
| include_in_schema | \`True\` | 是否进 OpenAPI |

### 注意

- k8s readiness 需业务自建并限制内网/鉴权
- 响应信封为 \`ApiResponse[dict]\`
`
</script>

<template>
  <DocPage :content="content" />
</template>
