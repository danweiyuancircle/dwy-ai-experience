<script setup lang="ts">
import { computed, provide } from 'vue'
import { cn } from '@/utils/cn'
import type { EChartContainerProps, ChartConfig } from './types'

const CHART_CONFIG_KEY = Symbol('chart-config')

const props = defineProps<EChartContainerProps>()

const chartId = computed(() => props.id ?? `chart-${Math.random().toString(36).slice(2)}`)

// Provide chart config for child components
provide(CHART_CONFIG_KEY, props.config)

// Build CSS variables from config colors
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
