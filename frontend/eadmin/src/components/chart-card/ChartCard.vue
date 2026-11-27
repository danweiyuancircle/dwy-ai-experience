<!--
  图表面板壳。
  不画图。标题右侧放切换，说明在图上方，图和表由页面放进默认插槽。
-->
<script setup lang="ts">
import { useSlots, type Slots } from 'vue'
import { ECard } from '@dwydev/eui'

defineOptions({ name: 'ChartCard' })

defineProps<{
  /** 卡片标题。示例：``'用户增长'``。 */
  title: string
  /** 图上方的一句说明。不传则不渲染。 */
  description?: string
}>()

// 声明生成不能从动态插槽模板反向推导自身，否则产生循环推断。
const slots: Slots = useSlots()
</script>

<template>
  <ECard :title="title">
    <template v-if="slots.extra" #title-extra>
      <slot name="extra" />
    </template>
    <p v-if="description" class="mb-3 text-xs text-muted-foreground">{{ description }}</p>
    <slot />
  </ECard>
</template>
