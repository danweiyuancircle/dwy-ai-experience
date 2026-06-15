<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import DocPage from '../../components/DocPage.vue'

const route = useRoute()
const name = computed(() => route.params.name as string)

const hookFiles = import.meta.glob('/../../dwy-cli/templates/claude-global/hooks/*', { eager: true, query: '?raw', import: 'default' }) as Record<string, string>

const hooks = computed(() => {
  const map: Record<string, string> = {}
  for (const [path, content] of Object.entries(hookFiles)) {
    const filename = path.split('/').pop()!.replace(/\.[^.]+$/, '')
    map[filename] = `# ${filename}\n\n## Hook 脚本源码\n\n\`\`\`bash\n${content}\n\`\`\`\n`
  }
  return map
})

const content = computed(() => hooks.value[name.value] || '# 未找到该 Hook')
const title = computed(() => name.value)
</script>

<template>
  <DocPage :content="content" :title="title" />
</template>
