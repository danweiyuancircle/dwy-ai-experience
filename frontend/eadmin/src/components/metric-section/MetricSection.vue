<!--
  概览里的一组指标。
  只渲染分组标题，卡片由默认插槽放进去。
-->
<script setup lang="ts">
defineOptions({ name: 'MetricSection' })

defineProps<{
  /** 分组名。示例：``'用户'``。 */
  title: string
}>()
</script>

<template>
  <section class="flex flex-col gap-3">
    <h2 class="text-sm font-medium text-muted-foreground">{{ title }}</h2>
    <slot />
  </section>
</template>
