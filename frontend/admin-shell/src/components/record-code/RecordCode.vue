<!--
  表格里的单号。
  只负责等宽和空值破折号。金额、时间、字节仍由页面格式化后传入。
-->
<script setup lang="ts">
import { computed } from 'vue'

defineOptions({ name: 'RecordCode' })

const props = withDefaults(
  defineProps<{
    /** 单号原文。空则显示占位。示例：``'P202610140001'``。 */
    text?: string | number | null
    /** 空值占位。默认 ``'—'``。示例：``'-'``。 */
    emptyText?: string
  }>(),
  { emptyText: '—' },
)

/** 空值换成占位，避免格子一片空白。 */
const display = computed(() => {
  if (props.text === null || props.text === undefined || props.text === '') return props.emptyText
  return String(props.text)
})

/** 占位用淡色，和有单号的等宽字分开。 */
const isEmpty = computed(() => display.value === props.emptyText)
</script>

<template>
  <span class="font-mono text-xs" :class="isEmpty ? 'text-muted-foreground' : undefined">{{ display }}</span>
</template>
