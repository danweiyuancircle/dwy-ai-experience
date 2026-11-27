<!-- 异步状态始终可读；失败后提供明确重试入口。 -->
<script setup lang="ts">
import { EAlert, EButton, ESpinner } from '@dwydev/eui'
defineOptions({ name: 'RequestFeedback' })

/** 页面负责发起请求；组件仅呈现加载或失败状态。 */
defineProps<{
  /** 加载优先于旧错误，防止重试时继续显示失败。 */
  loading?: boolean
  /** 已格式化、可直接展示给用户的失败说明。 */
  error?: string
}>()
/** 点击重试通知页面，不自行发起请求。 */
defineEmits<{ retry: [] }>()
</script>
<template>
  <div v-if="loading" class="flex items-center justify-center gap-3 py-10 text-sm text-muted-foreground" role="status"><ESpinner />正在加载…</div>
  <div v-else-if="error" class="flex flex-col items-start gap-3"><EAlert variant="destructive" :title="error" /><EButton variant="outline" size="sm" data-testid="retry" @click="$emit('retry')">重新加载</EButton></div>
</template>
