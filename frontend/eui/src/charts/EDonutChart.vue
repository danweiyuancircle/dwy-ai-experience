<script setup lang="ts">
import VisDonut, { VisDonutSelectors } from '@unovis/vue/components/donut'
import VisTooltip from '@unovis/vue/components/tooltip'
import VisSingleContainer from '@unovis/vue/containers/single-container'
import { usePreferredReducedMotion } from '@vueuse/core'
import { computed } from 'vue'
import { useConfigProvider } from '@/composables/useConfigProvider'
import ChartFrame from './ChartFrame.vue'
import { useChartColors } from './colors'
import type { EDonutChartItem, EDonutChartProps } from './types'

const props = withDefaults(defineProps<EDonutChartProps>(), {
  height: 240,
  loading: false,
})

const { locale } = useConfigProvider()
const motion = usePreferredReducedMotion()
const visible = computed(() => props.items.filter(item => Number.isFinite(item.value) && item.value >= 0))
const slices = computed(() => visible.value.filter(item => item.value > 0))
const total = computed(() => visible.value.reduce((sum, item) => sum + item.value, 0))
const colors = useChartColors(() => props.items)
const formatter = computed(() => new Intl.NumberFormat(locale.value.name))
const percentage = computed(() => new Intl.NumberFormat(locale.value.name, { style: 'percent', maximumFractionDigits: 1 }))
const share = (item: EDonutChartItem) => percentage.value.format(item.value / total.value)
const color = (item: EDonutChartItem) => colors.value.get(item.key)!
const id = (item: EDonutChartItem) => item.key
const value = (item: EDonutChartItem) => item.value
const formatValue = (value: number) => props.formatValue?.(value) ?? formatter.value.format(value)
const rows = computed(() => total.value > 0 ? visible.value.map(item => ({
  category: item.label,
  values: [formatValue(item.value), share(item)],
})) : [])
const tooltips = {
  [VisDonutSelectors.segment]: ({ data }: { data: EDonutChartItem }) => {
    const element = document.createElement('div')
    element.textContent = data.label + '  ' + formatValue(data.value) + ' (' + share(data) + ')'
    return element
  },
}
</script>

<template>
  <ChartFrame
    :label="label"
    :height="height"
    :loading="loading"
    :has-data="total > 0"
    :column-label="locale.chartCategory"
    :columns="[locale.chartValue, locale.chartShare]"
    :rows="rows"
  >
    <VisSingleContainer :data="slices" :height="height" :duration="motion === 'reduce' ? 0 : 180" aria-hidden="true">
      <VisDonut :id="id" :value="value" :color="color" :arc-width="22" :pad-angle="0.025" :central-label="formatValue(total)" />
      <VisTooltip :triggers="tooltips" />
    </VisSingleContainer>

    <template #legend>
      <ul class="text-muted-foreground flex flex-wrap gap-x-4 gap-y-1 text-xs">
        <li v-for="item in visible" :key="item.key" class="flex items-center gap-1.5">
          <span aria-hidden="true" class="size-2 rounded-xs" :style="{ backgroundColor: color(item) }" />
          {{ item.label }} {{ share(item) }}
        </li>
      </ul>
    </template>
  </ChartFrame>
</template>
