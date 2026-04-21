<script setup lang="ts">
import DocPage from '../../components/DocPage.vue'

const content = `
## hooks — Vue Composables

\`\`\`ts
import { useDebounce, useClickOutside, useEventListener } from '@dwydev/ekit'
\`\`\`

### useDebounce(value, delay?)

\`\`\`ts
const search = ref('')
const debouncedSearch = useDebounce(search, 300) // 默认 300ms
\`\`\`

返回防抖后的 \`Ref<T>\`，仅在源值停止变化 delay 毫秒后更新。

### useClickOutside(target, handler)

\`\`\`ts
const popoverRef = ref<HTMLElement | null>(null)
useClickOutside(popoverRef, () => { isOpen.value = false })
\`\`\`

点击 target 元素外部时触发 handler。自动在 onMounted/onBeforeUnmount 绑定/解绑。

### useEventListener(target, event, handler, options?)

\`\`\`ts
useEventListener(window, 'resize', onResize)
useEventListener(elementRef, 'scroll', onScroll, { passive: true })
\`\`\`

target 可以是 \`EventTarget\` 或 \`Ref<EventTarget>\`。自动在 onMounted/onBeforeUnmount 绑定/解绑。
`
</script>

<template>
  <DocPage :content="content" />
</template>
