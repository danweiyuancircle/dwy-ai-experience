<script setup lang="ts">
import DocPage from '../../components/DocPage.vue'

const content = `
## cache — 异步 Redis

\`\`\`python
from danweiyuan_eapi import cache
\`\`\`

| 函数 | 签名 | 说明 |
|------|------|------|
| cache.configure | \`(redis_url: str) -> None\` | 设置 Redis URL（启动时调用一次） |
| cache.get_redis | \`async () -> Redis\` | 获取/创建共享连接（未 configure 时抛 RuntimeError） |
| cache.close_redis | \`async () -> None\` | 关闭连接（安全幂等） |

### 使用示例

\`\`\`python
# lifespan 中初始化
@asynccontextmanager
async def lifespan(app: FastAPI):
    cache.configure(settings.redis_url)
    yield
    await cache.close_redis()

# 业务中使用
redis = await cache.get_redis()
await redis.set("key", "value", ex=3600)
val = await redis.get("key")
\`\`\`

### 设计要点

- **惰性连接：** \`configure\` 仅保存 URL，实际连接在首次 \`get_redis()\` 时建立
- **共享连接：** 全局共享一个 Redis 连接实例，避免重复创建
- **安全关闭：** \`close_redis\` 幂等，多次调用不会报错
- **前置检查：** 未调用 \`configure\` 时使用 \`get_redis\` 会抛出 \`RuntimeError\`

### 典型集成

\`\`\`python
# main.py
from contextlib import asynccontextmanager
from danweiyuan_eapi import cache

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动
    cache.configure(settings.redis_url)
    yield
    # 关闭
    await cache.close_redis()

app = FastAPI(lifespan=lifespan)
\`\`\`
`
</script>

<template>
  <DocPage :content="content" />
</template>
