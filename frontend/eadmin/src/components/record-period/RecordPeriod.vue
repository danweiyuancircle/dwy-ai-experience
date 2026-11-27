<!--
  账期筛选：快捷档 + 日期区间。
  快捷档选中后抛值，区间算哪一天由页面做。
  日期触发器默认撑满一行，这里收成内容宽度，才能和档位横排。
-->
<script setup lang="ts">
import { EDatePicker } from '@dwydev/eui'
import SegmentedFilter from '../segmented-filter/SegmentedFilter.vue'
import type { SegmentedOption } from '../segmented-filter/types'

defineOptions({ name: 'RecordPeriod' })

defineProps<{
  /** 左侧名字。示例：``'账期'``。 */
  label?: string
  /**
   * 当前快捷档。
   * 空串表示手选区间，两个档位都不亮。示例：``'this'``。
   */
  preset: string
  /** 快捷档。value 不能空。 */
  presets: SegmentedOption[]
  /** 已选闭区间。还没有时传 null。示例：``['2026-10-01', '2026-10-14']``。 */
  range?: [string, string] | null
  /**
   * 不可选的日期。返回 true 表示这一天禁用。
   * 不传则都能选。
   */
  disabledDate?: (date: Date) => boolean
}>()

const emit = defineEmits<{
  /** 点了一个快捷档。 */
  'update:preset': [value: string]
  /** 选完一段闭区间。只选了一头时不抛。 */
  'update:range': [value: [string, string]]
}>()

/**
 * 区间两头都有才交给页面。清空和只选开始日会被丢掉。
 * @param value 日期控件的值。单日或未完成的区间忽略。
 */
function onRange(value: string | [string, string] | undefined) {
  if (!Array.isArray(value) || !value[0] || !value[1]) return
  emit('update:range', [value[0], value[1]])
}
</script>

<template>
  <!-- contents：名字、档位、日期各自参加外层横排。 -->
  <div class="contents">
    <SegmentedFilter
      :label="label"
      :model-value="preset"
      :options="presets"
      @update:model-value="emit('update:preset', $event)"
    />
    <!-- 关掉清空：半截区间没有查询意义，触发器也不要撑满整行。 -->
    <EDatePicker
      class="w-auto shrink-0"
      :model-value="range ?? undefined"
      type="daterange"
      :clearable="false"
      :disabled-date="disabledDate"
      @change="onRange"
    />
  </div>
</template>
