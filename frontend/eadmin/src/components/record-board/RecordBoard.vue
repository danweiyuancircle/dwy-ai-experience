<!--
  明细页分区壳：说明、筛选、汇总、明细四段。
  只排位置。筛选项、说明文案、数字含义都由页面用 eui 填进插槽。
  明细区放页面自己的 PagedTable，空列表时上面三区仍在。
-->
<script setup lang="ts">
import { useSlots } from 'vue'
import { ECard } from '@dwydev/eui'

defineOptions({ name: 'RecordBoard' })

defineProps<{
  /** 汇总卡标题。示例：``"按当前筛选汇总"``。不传且没有汇总插槽时不渲染卡片。 */
  summaryTitle?: string
}>()

const slots = useSlots()
</script>

<template>
  <div class="record-board flex h-full min-h-0 w-full flex-col gap-3">
    <div v-if="slots.notice" class="record-board-notice">
      <slot name="notice" />
    </div>
    <!-- 筛选独立成条，不跟汇总数字挤在同一行。 -->
    <div v-if="slots.filters" class="record-board-filters rounded-lg bg-muted px-3 py-2">
      <slot name="filters" />
    </div>
    <ECard
      v-if="summaryTitle || slots.summary"
      class="record-board-summary"
      :title="summaryTitle"
    >
      <!-- 三项靠内容宽度，整组在卡内居中，避免贴在左侧留一大块空白。 -->
      <div
        v-if="slots.summary"
        class="record-board-metrics flex flex-wrap items-stretch justify-center divide-x divide-border"
      >
        <slot name="summary" />
      </div>
    </ECard>
    <div class="record-board-body flex min-h-0 flex-1 flex-col">
      <slot />
    </div>
  </div>
</template>
