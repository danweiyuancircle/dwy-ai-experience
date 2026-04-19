<script setup lang="ts">
import DocPage from '../../components/DocPage.vue'

const content = `
## pagination — 分页工具

\`\`\`python
from dwyeapi.pagination import PaginationParams, paginate, OffsetLimit
\`\`\`

### PaginationParams

FastAPI Depends 注入的查询参数模型。

| 字段 | 类型 | 默认 | 约束 |
|------|------|------|------|
| page | int | 1 | >= 1 |
| page_size | int | 20 | 1 ~ 100 |

### paginate(page, page_size) -> OffsetLimit

\`\`\`python
offset_limit = paginate(params.page, params.page_size)
# OffsetLimit(offset=0, limit=20) — 可直接用于 SQLAlchemy .offset().limit()
stmt = select(User).offset(offset_limit.offset).limit(offset_limit.limit)
\`\`\`

### 完整使用示例

\`\`\`python
from dwyeapi.pagination import PaginationParams, paginate
from dwyeapi.response import paginated

@router.get("/users")
async def list_users(
    params: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
):
    ol = paginate(params.page, params.page_size)
    stmt = select(User).offset(ol.offset).limit(ol.limit)
    result = await db.execute(stmt)
    users = result.scalars().all()

    count_stmt = select(func.count()).select_from(User)
    total = (await db.execute(count_stmt)).scalar_one()

    return paginated(
        [UserResponse.model_validate(u) for u in users],
        total,
        params.page,
        params.page_size,
    )
\`\`\`

### OffsetLimit

\`paginate\` 返回的命名元组/数据类，包含两个字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| offset | int | 跳过的记录数 |
| limit | int | 返回的记录数（等于 page_size） |
`
</script>

<template>
  <DocPage :content="content" />
</template>
