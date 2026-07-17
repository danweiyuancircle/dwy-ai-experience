<!--
  控制台页头区（hero）
  面包屑（多项时）+ AdminPageHeader 标题/描述，由 route.meta 驱动。
  meta.pageHero === false 或壳关闭 pageHero 时不渲染。
-->
<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAdminBreadcrumb } from '../composables/useAdminBreadcrumb'
import AdminBreadcrumb from './AdminBreadcrumb.vue'
import AdminPageHeader from './AdminPageHeader.vue'

const props = withDefaults(
  defineProps<{
    /**
     * 壳级默认是否展示 PageHero。
     * 单页 meta.pageHero 可覆盖。默认 true。
     */
    enabled?: boolean
  }>(),
  { enabled: true },
)

const route = useRoute()
const breadcrumbItems = useAdminBreadcrumb()

/** 最终是否渲染：壳开关 ∧ 路由未关闭 */
const isVisible = computed(() => {
  if (!props.enabled) return false
  if (route.meta.pageHero === false) return false
  return true
})

/** 页标题：优先当前路由 meta.title */
const title = computed(() => {
  const t = route.meta.title
  return typeof t === 'string' ? t : ''
})

/** 页描述 */
const description = computed(() => {
  const d = route.meta.description
  return typeof d === 'string' ? d : undefined
})

/** 多项才显示面包屑 */
const showBreadcrumb = computed(() => breadcrumbItems.value.length > 1)
</script>

<template>
  <div v-if="isVisible && title" class="mb-6 space-y-3" data-slot="admin-page-hero">
    <AdminBreadcrumb v-if="showBreadcrumb" :items="breadcrumbItems" />
    <AdminPageHeader :title="title" :description="description" />
  </div>
</template>
