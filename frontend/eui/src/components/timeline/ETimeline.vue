<!--
  ETimeline 时间线组件
  以左侧圆点 + 竖线连接的方式纵向展示事件列表；支持按类型（primary/success/warning/danger）着色
  reverse 切换后倒序展示，适用于「最新在顶部」的操作日志
-->
<script setup lang="ts">
import { computed } from 'vue'
import { cn } from '@/utils/cn'
import type { ETimelineProps, TimelineItem } from './types'

const props = withDefaults(defineProps<ETimelineProps>(), {
  items: () => [],
  reverse: false,
})

const displayItems = computed(() =>
  props.reverse ? [...props.items].reverse() : props.items
)

/**
 * 根据事件类型返回对应的圆点背景色 class
 */
function dotColor(type?: TimelineItem['type']) {
  switch (type) {
    case 'success': return 'bg-green-500'
    case 'warning': return 'bg-yellow-500'
    case 'danger': return 'bg-red-500'
    default: return 'bg-primary'
  }
}
</script>

<template>
  <div :class="cn('relative', props.class)">
    <div class="relative flex flex-col">
      <div
        v-for="(item, index) in displayItems"
        :key="index"
        class="relative flex gap-4 pb-8 last:pb-0"
      >
        <!-- Timeline connector + dot -->
        <div class="relative flex flex-col items-center">
          <div
            :class="cn('size-3 rounded-full ring-2 ring-background flex-shrink-0 mt-1', dotColor(item.type))"
          />
          <div
            v-if="index < displayItems.length - 1"
            class="w-px flex-1 bg-border mt-1"
          />
        </div>

        <!-- Content -->
        <div class="flex-1 min-w-0 pb-8 last:pb-0">
          <slot :name="`item-${index}`" :item="item">
            <div class="flex items-baseline justify-between gap-2">
              <p class="text-sm font-medium leading-none">{{ item.title }}</p>
              <time v-if="item.timestamp" class="text-xs text-muted-foreground whitespace-nowrap">
                {{ item.timestamp }}
              </time>
            </div>
            <p v-if="item.content" class="mt-1 text-sm text-muted-foreground">
              {{ item.content }}
            </p>
          </slot>
        </div>
      </div>
    </div>
  </div>
</template>
