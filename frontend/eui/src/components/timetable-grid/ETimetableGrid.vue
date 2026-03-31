<script setup lang="ts">
import { computed } from 'vue'
import { cn } from '@/utils/cn'
import type { ETimetableGridProps, TimetableItem } from './types'

const props = withDefaults(defineProps<ETimetableGridProps>(), {
  data: () => [],
  startHour: 8,
  endHour: 22,
  days: () => ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
})

const hours = computed(() => {
  const result: number[] = []
  for (let h = props.startHour; h <= props.endHour; h++) {
    result.push(h)
  }
  return result
})

const totalRows = computed(() => props.endHour - props.startHour)

function getItemStyle(item: TimetableItem): Record<string, string> {
  const rowStart = item.startHour - props.startHour + 2 // +2 for header row
  const rowSpan = item.endHour - item.startHour
  const colStart = item.day + 2 // +2 for time column
  return {
    gridRow: `${rowStart} / span ${rowSpan}`,
    gridColumn: `${colStart}`,
  }
}

const defaultColors = [
  'bg-blue-100 text-blue-800 border-blue-200',
  'bg-green-100 text-green-800 border-green-200',
  'bg-purple-100 text-purple-800 border-purple-200',
  'bg-yellow-100 text-yellow-800 border-yellow-200',
  'bg-red-100 text-red-800 border-red-200',
]

function getItemClasses(item: TimetableItem, index: number): string {
  if (item.color) return ''
  return defaultColors[index % defaultColors.length]
}
</script>

<template>
  <div
    data-slot="timetable-grid"
    :class="cn('overflow-auto', props.class)"
  >
    <div
      class="grid min-w-max"
      :style="{
        gridTemplateColumns: `4rem repeat(${days.length}, 1fr)`,
        gridTemplateRows: `2rem repeat(${totalRows}, 3rem)`,
      }"
    >
      <!-- Top-left empty cell -->
      <div class="border-b border-r bg-muted/50" />

      <!-- Day headers -->
      <div
        v-for="day in days"
        :key="day"
        class="flex items-center justify-center border-b border-r bg-muted/50 text-xs font-medium text-muted-foreground"
      >
        {{ day }}
      </div>

      <!-- Time labels -->
      <template v-for="hour in hours" :key="hour">
        <div
          v-if="hour < endHour"
          class="flex items-start justify-center border-b border-r pt-1 text-xs text-muted-foreground"
        >
          {{ String(hour).padStart(2, '0') }}:00
        </div>
      </template>

      <!-- Day column cells (background grid) -->
      <template v-for="(day, dayIdx) in days" :key="`col-${dayIdx}`">
        <div
          v-for="hour in hours.slice(0, -1)"
          :key="`cell-${dayIdx}-${hour}`"
          class="border-b border-r"
          :style="{
            gridRow: `${hour - startHour + 2}`,
            gridColumn: `${dayIdx + 2}`,
          }"
        />
      </template>

      <!-- Timetable items -->
      <div
        v-for="(item, idx) in data"
        :key="`item-${idx}`"
        :style="{ ...getItemStyle(item), backgroundColor: item.color || undefined }"
        :class="cn(
          'z-10 m-0.5 overflow-hidden rounded border p-1 text-xs',
          !item.color ? getItemClasses(item, idx) : 'text-white border-transparent',
        )"
      >
        <div class="font-medium leading-tight line-clamp-2">{{ item.title }}</div>
        <div class="mt-0.5 opacity-70">
          {{ String(item.startHour).padStart(2, '0') }}:00 - {{ String(item.endHour).padStart(2, '0') }}:00
        </div>
      </div>
    </div>
  </div>
</template>
