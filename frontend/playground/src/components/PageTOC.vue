<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'

export interface TOCItem {
  id: string
  label: string
}

const props = defineProps<{ items: TOCItem[] }>()
const activeId = ref('')

let observer: IntersectionObserver | null = null

onMounted(() => {
  nextTick(() => {
    observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            activeId.value = entry.target.id
          }
        }
      },
      { rootMargin: '-80px 0px -60% 0px', threshold: 0.1 },
    )
    for (const item of props.items) {
      const el = document.getElementById(item.id)
      if (el) observer.observe(el)
    }
  })
})

onBeforeUnmount(() => {
  observer?.disconnect()
})

function scrollTo(id: string) {
  const el = document.getElementById(id)
  if (el) {
    el.scrollIntoView({ behavior: 'smooth', block: 'start' })
    activeId.value = id
  }
}
</script>

<template>
  <nav class="space-y-1">
    <button
      v-for="item in items"
      :key="item.id"
      :class="[
        'block w-full text-left px-3 py-1 rounded text-xs transition-colors truncate',
        activeId === item.id
          ? 'text-primary font-medium bg-primary/5'
          : 'text-muted-foreground hover:text-foreground',
      ]"
      @click="scrollTo(item.id)"
    >
      {{ item.label }}
    </button>
  </nav>
</template>
