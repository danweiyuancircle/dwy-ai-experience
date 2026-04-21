<!--
  EChartContainer 图表容器组件
  将 ChartConfig 注入为 CSS 变量与 provide 上下文，供图表子组件读取
  本身不绘制图表，仅提供统一的尺寸与主题色容器
-->
<script setup lang="ts">
import { computed, provide } from 'vue'
import { cn } from '@/utils/cn'
import type { EChartContainerProps, ChartConfig } from './types'

const CHART_CONFIG_KEY = Symbol('chart-config')

const props = defineProps<EChartContainerProps>()

// 未显式传入 id 时生成随机 id，便于多个图表共存时的样式隔离
const chartId = computed(() => props.id ?? `chart-${Math.random().toString(36).slice(2)}`)

// 通过 provide 将图表配置向下传递给子组件（如 tooltip、legend）
provide(CHART_CONFIG_KEY, props.config)

// 将配置中的 color 转为 --color-{key} CSS 变量，供子组件用 var() 消费
const colorVars = computed(() => {
  const vars: Record<string, string> = {}
  for (const [key, value] of Object.entries(props.config)) {
    if (value.color) {
      vars[`--color-${key}`] = value.color
    }
  }
  return vars
})
</script>

<template>
  <div
    data-slot="chart"
    :data-chart="chartId"
    :class="cn(
      'flex flex-col aspect-video justify-center text-xs h-full w-full',
      props.class,
    )"
    :style="colorVars"
  >
    <slot :id="chartId" :config="config" />
  </div>
</template>
