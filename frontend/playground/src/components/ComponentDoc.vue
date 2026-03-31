<script setup lang="ts">
import PageTOC from './PageTOC.vue'
import type { TOCItem } from './PageTOC.vue'

defineProps<{
  title: string
  description: string
  tocItems: TOCItem[]
}>()
</script>

<template>
  <div class="flex gap-6">
    <!-- Main content -->
    <div class="flex-1 min-w-0 max-w-4xl">
      <h1 class="text-2xl font-bold mb-2">{{ title }}</h1>
      <p class="text-muted-foreground mb-8">{{ description }}</p>
      <div class="space-y-8">
        <slot />
      </div>
    </div>

    <!-- Right TOC -->
    <div class="hidden xl:block w-[180px] shrink-0">
      <div class="sticky top-4">
        <p class="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2 px-3">目录</p>
        <PageTOC :items="tocItems" />
      </div>
    </div>
  </div>
</template>
