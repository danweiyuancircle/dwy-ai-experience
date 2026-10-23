<!--
  状态徽章。
  只锁外形和七档色，文案由页面传入。
-->
<script setup lang="ts">
import { EBadge } from '@dwydev/eui'
import { STATUS_TONE, type StatusTone } from './tone'

defineOptions({ name: 'StatusBadge' })

defineProps<{
  /** 七档色。枚举见 ``StatusTone``。示例：``'active'``。 */
  tone: StatusTone
  /** 徽章文案。示例：``'正常'``。 */
  label: string
}>()
</script>

<template>
  <EBadge variant="outline" :class="STATUS_TONE[tone]" class="font-normal">
    {{ label }}
  </EBadge>
</template>
