<script setup lang="ts">
import VisAxis from '@unovis/vue/components/axis'
import VisCrosshair from '@unovis/vue/components/crosshair'
import VisGroupedBar from '@unovis/vue/components/grouped-bar'
import VisLine from '@unovis/vue/components/line'
import VisTooltip from '@unovis/vue/components/tooltip'
import VisXYContainer from '@unovis/vue/containers/xy-container'
import { usePreferredReducedMotion } from '@vueuse/core'
import { computed } from 'vue'
import { useConfigProvider } from '@/composables/useConfigProvider'
import ChartFrame from './ChartFrame.vue'
import { useChartColors } from './colors'
import type { ECartesianChartProps } from './types'

const props = withDefaults(defineProps<ECartesianChartProps & { kind: 'line' | 'bar' }>(), {
  height: 240,
  loading: false,
})

interface Row {
  index: number
  category: string
  values: (number | null)[]
}

const { locale } = useConfigProvider()
const motion = usePreferredReducedMotion()
const palette = useChartColors(() => props.series)
const colors = computed(() => props.series.map(series => palette.value.get(series.key)!))
const formatter = computed(() => new Intl.NumberFormat(locale.value.name))
const formatValue = (value: number) => props.formatValue?.(value) ?? formatter.value.format(value)
const formatCell = (value: number | null) => value === null ? '—' : formatValue(value)
const labels = computed(() => props.series.map(series => series.label))
const rows = computed<Row[]>(() => props.categories.map((category, index) => ({
  index,
  category,
  values: props.series.map((series) => {
    const value = series.values[index]
    return typeof value === 'number' && Number.isFinite(value) ? value : null
  }),
})))
const hasData = computed(() => rows.value.some(row => row.values.some(value => value !== null)))
const table = computed(() => rows.value.map(row => ({ category: row.category, values: row.values.map(formatCell) })))
// Unovis 识别 NaN 为断点，但会把 null 当作零值。
const accessors = computed(() => props.series.map((_, index) => (row: Row) => row.values[index] ?? NaN))
const x = (row: Row) => row.index
const seriesColor = (_: Row, index: number) => colors.value[index]
const axisLabel = (value: number | Date) => typeof value === 'number' ? props.categories[value] ?? '' : ''
const axisValue = (value: number | Date) => typeof value === 'number' ? formatValue(value) : ''
const ticks = computed(() => {
  const last = props.categories.length - 1
  const intervals = Math.min(last, 5)
  return intervals > 0 ? Array.from({ length: intervals + 1 }, (_, index) => Math.round(index * last / intervals)) : [0]
})

function tooltip(row: Row) {
  const element = document.createElement('div')
  element.className = 'whitespace-pre-line'
  element.textContent = [row.category, ...row.values.map((value, index) =>
    labels.value[index] + '  ' + formatCell(value),
  )].join('\n')
  return element
}
</script>

<template>
  <ChartFrame
    :label="label"
    :height="height"
    :loading="loading"
    :has-data="hasData"
    :column-label="locale.chartCategory"
    :columns="labels"
    :rows="table"
  >
    <VisXYContainer
      v-if="hasData"
      :data="rows"
      :height="height"
      :duration="motion === 'reduce' ? 0 : 180"
      :padding="{ top: 8, right: 12, bottom: 4, left: 4 }"
      aria-hidden="true"
    >
      <VisAxis type="x" :tick-values="ticks" :tick-format="axisLabel" :grid-line="false" />
      <VisAxis type="y" :tick-format="axisValue" :num-ticks="4" :domain-line="false" />
      <template v-if="kind === 'line'">
        <VisLine
          v-for="(serie, index) in series"
          :key="serie.key"
          :x="x"
          :y="accessors[index]"
          :color="colors[index]"
          :line-dash-array="index % 2 ? [5, 4] : undefined"
        />
      </template>
      <VisGroupedBar v-else :x="x" :y="accessors" :color="seriesColor" :rounded-corners="3" />
      <VisCrosshair :template="tooltip" :color="seriesColor" />
      <VisTooltip />
    </VisXYContainer>

    <template #legend>
      <ul class="text-muted-foreground flex flex-wrap gap-x-4 gap-y-1 text-xs">
        <li v-for="(serie, index) in series" :key="serie.key" class="flex items-center gap-1.5">
          <span
            aria-hidden="true"
            class="w-3.5 border-t-2"
            :class="{ 'border-dashed': kind === 'line' && index % 2 }"
            :style="{ borderColor: colors[index] }"
          />
          {{ serie.label }}
        </li>
      </ul>
    </template>
  </ChartFrame>
</template>
