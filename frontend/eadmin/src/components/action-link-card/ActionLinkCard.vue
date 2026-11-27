<!--
  快捷入口卡。
  整卡跳转。外壳与指标卡相同，这里只放标题和一行说明。
-->
<script setup lang="ts">
import OverviewCard from '../overview-card/OverviewCard.vue'

defineOptions({ name: 'ActionLinkCard' })

defineProps<{
  /** 入口标题。示例：``'API Key'``。 */
  title: string
  /** 一行说明。示例：``'创建或管理密钥'``。 */
  description: string
  /** 点击跳转的路径。示例：``'/keys'``。 */
  to: string
}>()
</script>

<template>
  <OverviewCard :to="to">
    <h3 class="text-base font-semibold">{{ title }}</h3>
    <p class="mt-1.5 text-sm leading-relaxed text-muted-foreground">{{ description }}</p>
    <template v-if="$slots.icon" #icon>
      <slot name="icon" />
    </template>
  </OverviewCard>
</template>
