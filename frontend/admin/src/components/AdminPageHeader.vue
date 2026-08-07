<!--
  页头标题（内置）
  仅 title + 可选 description，样式走 eui 语义 token。
-->
<script setup lang="ts">
/** AdminPageHeader props */
defineProps<{
  /** 页面主标题 */
  title: string
  /** 副标题/描述，省略时不渲染 */
  description?: string
}>()
</script>

<template>
  <div class="space-y-1" data-slot="admin-page-header">
    <h1 class="text-2xl font-semibold tracking-tight">{{ title }}</h1>
    <p v-if="description" class="text-sm text-muted-foreground">{{ description }}</p>
  </div>
</template>
