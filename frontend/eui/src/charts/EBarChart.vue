<script setup lang="ts">
import CartesianChart from './CartesianChart.vue'
import type { ECartesianChartProps } from './types'

const props = defineProps<ECartesianChartProps>()
</script>

<template>
  <CartesianChart v-bind="props" kind="bar" />
</template>
