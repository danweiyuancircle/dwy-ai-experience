<script setup lang="ts">
import { useConfigProvider } from '@/composables/useConfigProvider'

defineProps<{
  label: string
  height: number
  loading: boolean
  hasData: boolean
  columnLabel: string
  columns: readonly string[]
  rows: ReadonlyArray<{ category: string; values: readonly string[] }>
}>()

const { locale } = useConfigProvider()
</script>

<template>
  <figure data-slot="chart" class="eui-chart min-w-0" :aria-label="label" :aria-busy="loading">
    <div data-slot="chart-plot" :style="{ minHeight: height + 'px' }" class="relative flex min-w-0 flex-col justify-center">
      <p v-if="loading" role="status" class="text-muted-foreground text-center text-sm">
        {{ locale.loading }}
      </p>
      <slot v-else-if="hasData" />
      <p v-else class="text-muted-foreground text-center text-sm">{{ locale.empty }}</p>
    </div>
    <template v-if="!loading && hasData">
      <slot name="legend" />
      <details class="mt-2 text-sm">
        <summary class="text-muted-foreground cursor-pointer">{{ locale.chartData }}</summary>
        <div class="mt-2 overflow-x-auto">
          <table class="w-full text-left text-sm" :aria-label="label">
            <thead>
              <tr class="border-b">
                <th scope="col" class="p-2">{{ columnLabel }}</th>
                <th v-for="(column, index) in columns" :key="index" scope="col" class="p-2">{{ column }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, index) in rows" :key="index" class="border-b last:border-b-0">
                <th scope="row" class="p-2 font-normal">{{ row.category }}</th>
                <td v-for="(value, i) in row.values" :key="i" class="p-2 tabular-nums">{{ value }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </details>
    </template>
  </figure>
</template>
