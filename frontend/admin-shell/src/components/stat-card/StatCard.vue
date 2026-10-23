<!--
  一张指标卡。
  标题和数值由页面算好传入。外壳、图标井和可点箭头在 OverviewCard。
-->
<script setup lang="ts">
import { EStatistic } from '@dwydev/eui'
import OverviewCard from '../overview-card/OverviewCard.vue'

defineOptions({ name: 'StatCard' })

defineProps<{
  /** 指标名。示例：``'今日注册'``。 */
  title: string
  /** 已格式化的值。示例：``128`` 或 ``'1.2 MB'``。 */
  value: string | number
  /** 点击跳转的路径。不传则不可点。示例：``'/admin/users'``。 */
  to?: string
}>()
</script>

<template>
  <OverviewCard :to="to">
    <EStatistic :title="title" :value="value" />
    <template v-if="$slots.icon" #icon>
      <slot name="icon" />
    </template>
  </OverviewCard>
</template>
