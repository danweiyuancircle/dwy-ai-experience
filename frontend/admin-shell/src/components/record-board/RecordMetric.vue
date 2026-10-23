<!--
  汇总卡里的一个数字。
  标签和值由页面算好传入。danger 只在需要提醒时用，例如失败数大于 0。
-->
<script setup lang="ts">
import { EStatistic } from '@dwydev/eui'

defineOptions({ name: 'RecordMetric' })

withDefaults(
  defineProps<{
    /** 指标名。示例：``"请求次数"``。 */
    label: string
    /** 已格式化的值。数字走千分位，字符串原样。示例：``"1.2 MB"``。 */
    value: string | number
    /**
     * 数值强调。
     * 枚举 ``{'default', 'danger'}``，默认 ``'default'``。
     */
    tone?: 'default' | 'danger'
  }>(),
  { tone: 'default' },
)
</script>

<template>
  <EStatistic
    class="items-center px-8 text-center"
    :class="tone === 'danger' ? 'text-destructive' : undefined"
    :title="label"
    :value="value"
  />
</template>
