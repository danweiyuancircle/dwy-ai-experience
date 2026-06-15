<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import DocPage from '../../components/DocPage.vue'

const route = useRoute()
const name = computed(() => route.params.name as string)

const ruleFiles = import.meta.glob('/../../dwy-cli/templates/claude-global/rules/*.md', { eager: true, query: '?raw', import: 'default' }) as Record<string, string>

const rules = computed(() => {
  const map: Record<string, string> = {}
  for (const [path, content] of Object.entries(ruleFiles)) {
    const filename = path.split('/').pop()!.replace('.md', '')
    map[filename] = content
  }
  return map
})

const content = computed(() => rules.value[name.value] || '# 未找到该 Rule')
const title = computed(() => name.value)
</script>

<template>
  <DocPage :content="content" :title="title" />
</template>
