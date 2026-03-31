<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import DocPage from '../../components/DocPage.vue'

const route = useRoute()
const name = computed(() => route.params.name as string)

const skillFiles = import.meta.glob('/../../claude-cli/templates/claude-global/skills/*/SKILL.md', { eager: true, query: '?raw', import: 'default' }) as Record<string, string>

const skills = computed(() => {
  const map: Record<string, string> = {}
  for (const [path, content] of Object.entries(skillFiles)) {
    const parts = path.split('/')
    const dirName = parts[parts.length - 2]
    // Strip YAML frontmatter
    const stripped = content.replace(/^---[\s\S]*?---\n*/, '')
    map[dirName] = stripped
  }
  return map
})

const content = computed(() => skills.value[name.value] || '# 未找到该 Skill')
const title = computed(() => name.value)
</script>

<template>
  <DocPage :content="content" :title="title" />
</template>
