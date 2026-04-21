<script setup lang="ts">
import DocPage from '../../components/DocPage.vue'

const content = `
## storage — localStorage 封装

\`\`\`ts
import { useStorage, storage } from '@dwydev/ekit'
\`\`\`

### useStorage(key, defaultValue) — 响应式

返回 Vue \`Ref<T>\`，自动 JSON 序列化，深度 watch 自动同步。设为 null/undefined 时自动 removeItem。

\`\`\`ts
const token = useStorage<string>('token', '')
const config = useStorage<{ theme: string }>('config', { theme: 'light' })
\`\`\`

### storage — 静态工具对象

| 方法 | 签名 | 说明 |
|------|------|------|
| get | \`get<T>(key, defaultValue?): T \\| undefined\` | JSON 解析失败时返回原始字符串 |
| set | \`set(key, value): void\` | JSON.stringify 后存储 |
| remove | \`remove(key): void\` | 删除指定 key |
| clear | \`clear(): void\` | 清空全部 |
`
</script>

<template>
  <DocPage :content="content" />
</template>
