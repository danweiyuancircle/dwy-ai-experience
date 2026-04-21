<!--
  ECard 卡片组件
  提供 header / content / footer 三段式结构
  header 支持标题 / 描述 / 右侧操作按钮（action 插槽）
-->
<script setup lang="ts">
import { cn } from '@/utils/cn'
import type { ECardProps } from './types'

const props = defineProps<ECardProps>()

/**
 * 判断是否存在 header 区域内容（含标题、描述、action 插槽）
 */
const hasHeader = (slots: Record<string, unknown>) =>
  !!(slots.header || slots.title || slots.action || props.title || props.description)
</script>

<template>
  <div
    data-slot="card"
    :class="cn('bg-card text-card-foreground flex flex-col gap-6 rounded-xl border py-6 shadow-sm', props.class)"
  >
    <!-- header -->
    <slot name="header">
      <div
        v-if="title || description || $slots.title || $slots.action"
        data-slot="card-header"
        class="@container/card-header grid auto-rows-min grid-rows-[auto_auto] items-start gap-1.5 px-6 has-data-[slot=card-action]:grid-cols-[1fr_auto] [.border-b]:pb-6"
      >
        <h3
          v-if="title || $slots.title"
          data-slot="card-title"
          class="leading-none font-semibold"
        >
          <slot name="title">{{ title }}</slot>
        </h3>
        <p
          v-if="description || $slots.description"
          data-slot="card-description"
          class="text-muted-foreground text-sm"
        >
          <slot name="description">{{ description }}</slot>
        </p>
        <div
          v-if="$slots.action"
          data-slot="card-action"
          class="col-start-2 row-span-2 row-start-1 self-start justify-self-end"
        >
          <slot name="action" />
        </div>
      </div>
    </slot>

    <!-- content -->
    <div
      v-if="$slots.default"
      data-slot="card-content"
      class="px-6"
    >
      <slot />
    </div>

    <!-- footer -->
    <div
      v-if="$slots.footer"
      data-slot="card-footer"
      class="flex items-center px-6 [.border-t]:pt-6"
    >
      <slot name="footer" />
    </div>
  </div>
</template>
