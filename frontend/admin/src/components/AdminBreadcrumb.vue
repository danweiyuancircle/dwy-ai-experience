<!--
  SPA 面包屑
  eui EBreadcrumb 使用原生 a[href] 会导致整页刷新，故用 router-link 自绘同视觉结构。
  仅一项时调用方应隐藏本组件。
-->
<script setup lang="ts">
import { ChevronRight } from 'lucide-vue-next'
import type { AdminBreadcrumbItem } from '../model/types'

/** AdminBreadcrumb props */
defineProps<{
  /** 面包屑数据；长度建议 ≥ 2 再展示 */
  items: AdminBreadcrumbItem[]
}>()
</script>

<template>
  <nav aria-label="breadcrumb" data-slot="admin-breadcrumb">
    <ol class="text-muted-foreground flex flex-wrap items-center gap-1.5 text-sm break-words sm:gap-2.5">
      <template v-for="(item, index) in items" :key="`${item.label}-${index}`">
        <li
          v-if="index > 0"
          role="presentation"
          aria-hidden="true"
          class="[&>svg]:size-3.5"
        >
          <ChevronRight class="size-3.5" />
        </li>
        <li class="inline-flex items-center gap-1.5">
          <span
            v-if="index === items.length - 1 || !item.to"
            role="link"
            aria-disabled="true"
            aria-current="page"
            class="text-foreground font-normal"
          >
            {{ item.label }}
          </span>
          <router-link
            v-else
            :to="item.to"
            class="hover:text-foreground transition-colors"
          >
            {{ item.label }}
          </router-link>
        </li>
      </template>
    </ol>
  </nav>
</template>
