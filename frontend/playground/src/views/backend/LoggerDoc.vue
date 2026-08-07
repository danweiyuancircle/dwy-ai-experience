<script setup lang="ts">
import DocPage from '../../components/DocPage.vue'

const content = `
## logger — 全局日志

\`\`\`python
from dwyeapi import logger
# 或 from dwyeapi.logger import configure, get_logger, close
\`\`\`

基于 loguru：彩色控制台 + 按天/大小轮转文件，可拦截 stdlib logging。

| API | 说明 |
|-----|------|
| logger.configure(...) | 应用启动时调用一次 |
| logger.get_logger(name) | 获取命名 logger |
| logger.close() | 关闭 sink（lifespan 退出时） |

### 配置示例

\`\`\`python
from contextlib import asynccontextmanager
from dwyeapi import logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.configure(
        level=settings.log_level,
        # 其它参数见源码：log 目录、JSON、拦截 stdlib 等
    )
    yield
    logger.close()

log = logger.get_logger(__name__)
log.info("hello %s", "world")  # 使用 % 占位符，与 stdlib 一致
\`\`\`

### 设计要点

- 消息用 \`%s\` / \`%d\` 等 stdlib 占位符，位置参数延迟格式化
- 支持 \`exc_info=True\` 记录异常堆栈
- 默认保留天数、单文件大小上限等由 configure 参数控制
`
</script>

<template>
  <DocPage :content="content" />
</template>
