<script setup lang="ts">
import DocPage from '../../components/DocPage.vue'

const content = `
## dt — 时间工具

\`\`\`python
from dwyeapi import dt
\`\`\`

业务时间统一 **Asia/Shanghai**；JWT 等协议场景用 UTC 方法。

**禁止**业务代码直接 \`datetime.now()\` / \`datetime.utcnow()\` / \`from datetime import timedelta\`。

### 常用 API

| API | 说明 |
|-----|------|
| dt.now() | naive 中国时间（写库） |
| dt.now_str() | \`"2026-04-06 14:30:00"\` |
| dt.today() | 当前中国日期 |
| dt.timestamp() | Unix 秒 |
| dt.utc_now() | aware UTC（JWT） |
| dt.timedelta(...) | 透传 stdlib timedelta |
| dt.after(**kwargs) | now + 偏移（naive 中国时间） |
| dt.before(**kwargs) | now - 偏移 |
| dt.utc_after(**kwargs) | utc_now + 偏移 |
| dt.utc_before(**kwargs) | utc_now - 偏移 |

### 示例

\`\`\`python
from dwyeapi import dt

created = dt.now()
expires = dt.utc_after(minutes=30)  # JWT exp
deadline = dt.after(days=1)
delta = dt.timedelta(hours=2)
\`\`\`
`
</script>

<template>
  <DocPage :content="content" />
</template>
