<!--
  单选分段。
  点掉当前项时切换组会给出空串，这里丢掉，避免筛选被点没。
  外部仍可以把 modelValue 设成空串，用来表示「没有档位命中」（手选日期就是这样）。
-->
<script setup lang="ts">
import { EToggleGroup, EToggleGroupItem } from '@dwydev/eui'
import type { SegmentedOption } from './types'

defineOptions({ name: 'SegmentedFilter' })

defineProps<{
  /** 当前值。可以是空串，表示没有档位命中。示例：``'active'``。 */
  modelValue: string
  /** 可选项。至少一项，value 不能空。 */
  options: SegmentedOption[]
  /** 档位左侧的名字。不传则只有切换组。示例：``'账期'``。 */
  label?: string
}>()

const emit = defineEmits<{
  /** 选中另一项。空串不向外抛。 */
  'update:modelValue': [value: string]
}>()

/**
 * 拼出档位文案。有计数时跟在后面，0 也保留。
 * @param option 一个档位。
 * @returns 按钮上的字。示例：``'正常 12'``。
 */
function optionLabel(option: SegmentedOption): string {
  if (option.count === undefined) return option.label
  return `${option.label} ${option.count}`
}

/**
 * 切换组取消选中时给出空串，保持原值。
 * @param value 新值。空串或空表示取消。
 */
function onChange(value: string | string[] | undefined | null) {
  if (typeof value !== 'string' || value === '') return
  emit('update:modelValue', value)
}
</script>

<template>
  <!-- contents：标签和切换组各自参加外层横排，不另起一块把日期挤下去。 -->
  <div class="contents">
    <span v-if="label" class="text-sm text-muted-foreground">{{ label }}</span>
    <!--
      白底轨道 + 主色选中。
      默认选中是 bg-accent，放在筛选条的 bg-muted 上几乎同色，点了看不出哪一档。
    -->
    <EToggleGroup
      :model-value="modelValue"
      type="single"
      size="sm"
      class="rounded-md bg-background p-0.5"
      @update:model-value="onChange"
    >
      <EToggleGroupItem
        v-for="option in options"
        :key="option.value"
        :value="option.value"
        class="data-[state=on]:bg-primary data-[state=on]:text-primary-foreground"
      >
        {{ optionLabel(option) }}
      </EToggleGroupItem>
    </EToggleGroup>
  </div>
</template>
