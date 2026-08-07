<script setup lang="ts">
import DocPage from '../../components/DocPage.vue'

const content = `
## tasks — 异步任务（ARQ）

\`\`\`python
pip install "dwyeapi[tasks]"

from dwyeapi.tasks import setup_tasks, task_router, register, TaskContext, create_worker_settings
\`\`\`

### 快速开始

\`\`\`python
from dwyeapi.tasks import register, TaskContext, setup_tasks, task_router

@register("process_data")
async def process_data(ctx: TaskContext, params: dict):
    await ctx.log("Processing...")
    await ctx.update_progress(50)
    return {"done": True}

# lifespan
await setup_tasks(app, settings, session_factory)
app.include_router(task_router)

# worker
# arq app.worker.WorkerSettings  （create_worker_settings 生成）
\`\`\`

### HTTP 端点（task_router）

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /tasks | 提交任务 |
| GET | /tasks/{task_id} | 查询任务 |
| GET | /tasks | 列表（分页 + 筛选，page_size ≤ 100） |
| POST | /tasks/{task_id}/cancel | 协作式取消（写 Redis 标记，worker 检查） |

### 请求约束（TaskCreate）

| 字段 | 约束 |
|------|------|
| task_type | 1–50 字符（与 ORM 列对齐） |
| params | dict，最多 50 个键 |

### 响应信封

成功 \`code\` 为 \`"SUCCESS"\`（字符串），不是数字 200：

\`\`\`json
{
  "code": "SUCCESS",
  "message": "success",
  "data": { "id": "...", "status": "pending", "progress": 0 },
  "timestamp": 1775000000
}
\`\`\`

### 安全注意

- \`task_router\` **默认无鉴权**，生产务必挂 Depends(auth) 或内网暴露
- 取消已结束任务抛 \`BusinessError\` → HTTP **422**（非 400）
- 完整集成见仓库 \`docs/tasks-integration-guide.md\`
`
</script>

<template>
  <DocPage :content="content" />
</template>
