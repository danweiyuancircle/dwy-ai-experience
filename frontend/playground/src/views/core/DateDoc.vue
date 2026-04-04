<script setup lang="ts">
import DocPage from '../../components/DocPage.vue'

const content = `
## date — 日期格式化

\`\`\`ts
import { formatDate, formatDateTime, formatTime, formatRelativeTime } from '@danweiyuan/ekit'
\`\`\`

所有函数接收 \`string | number | Date\` 类型输入。

| 函数 | 输出格式 | 示例 |
|------|---------|------|
| formatDate | \`YYYY-MM-DD\` | \`2025-03-15\` |
| formatDateTime | \`YYYY-MM-DD HH:mm:ss\` | \`2025-03-15 14:30:00\` |
| formatTime | \`HH:mm\` | \`14:30\` |
| formatRelativeTime | 中文相对时间 | \`刚刚\` / \`5 分钟前\` / \`3 小时前\` / \`7 天前\` / 超过 30 天返回 \`toLocaleDateString('zh-CN')\` |
`
</script>

<template>
  <DocPage :content="content" />
</template>
