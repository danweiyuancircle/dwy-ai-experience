<script setup lang="ts">
import { computed, ref } from 'vue'
import { CalendarDays, ChevronLeft, ChevronRight, X } from 'lucide-vue-next'
import {
  CalendarCell,
  CalendarCellTrigger,
  CalendarGrid,
  CalendarGridBody,
  CalendarGridHead,
  CalendarGridRow,
  CalendarHeadCell,
  CalendarHeader,
  CalendarHeading,
  CalendarNext,
  CalendarPrev,
  CalendarRoot,
  PopoverAnchor,
  PopoverContent,
  PopoverPortal,
  PopoverRoot,
  PopoverTrigger,
} from 'reka-ui'
import { getLocalTimeZone, parseDate, today, CalendarDate } from '@internationalized/date'
import { cn } from '@/utils/cn'
import type { EDatePickerProps, EDatePickerEmits } from './types'

const props = withDefaults(defineProps<EDatePickerProps>(), {
  placeholder: 'Pick a date',
  disabled: false,
  clearable: false,
  format: 'YYYY-MM-DD',
})

const emit = defineEmits<EDatePickerEmits>()

const open = ref(false)

/** Parse the incoming modelValue into a CalendarDate */
const calendarValue = computed(() => {
  if (!props.modelValue) return undefined
  try {
    const d = props.modelValue instanceof Date ? props.modelValue : new Date(props.modelValue)
    if (isNaN(d.getTime())) return undefined
    return new CalendarDate(d.getFullYear(), d.getMonth() + 1, d.getDate())
  } catch {
    return undefined
  }
})

/** Format CalendarDate using the format prop (supports YYYY, MM, DD tokens) */
function formatDate(date: CalendarDate): string {
  const y = String(date.year)
  const m = String(date.month).padStart(2, '0')
  const d = String(date.day).padStart(2, '0')
  return props.format
    .replace('YYYY', y)
    .replace('MM', m)
    .replace('DD', d)
}

/** Display string shown in the trigger */
const displayValue = computed(() => {
  if (!calendarValue.value) return ''
  return formatDate(calendarValue.value)
})

function onSelect(val: any) {
  if (!val) return
  const str = formatDate(val as CalendarDate)
  emit('update:modelValue', str)
  emit('change', str)
  open.value = false
}

function onClear(e: MouseEvent) {
  e.stopPropagation()
  emit('update:modelValue', undefined)
  emit('change', undefined)
}
</script>

<template>
  <PopoverRoot v-model:open="open">
    <PopoverAnchor as-child>
      <PopoverTrigger as-child>
        <button
          :disabled="disabled"
          :class="cn(
            'flex h-9 w-full items-center justify-between rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-xs ring-offset-background',
            'focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2',
            'disabled:cursor-not-allowed disabled:opacity-50',
            !displayValue && 'text-muted-foreground',
            props.class,
          )"
        >
          <span class="flex items-center gap-2">
            <CalendarDays class="size-4 shrink-0 opacity-50" />
            {{ displayValue || placeholder }}
          </span>
          <X
            v-if="clearable && displayValue"
            class="size-4 shrink-0 opacity-50 hover:opacity-100"
            @click.stop="onClear"
          />
        </button>
      </PopoverTrigger>
    </PopoverAnchor>

    <PopoverPortal>
      <PopoverContent
        :side-offset="4"
        align="start"
        :class="cn(
          'z-50 rounded-md border bg-popover p-0 text-popover-foreground shadow-md outline-none',
          'data-[state=open]:animate-in data-[state=closed]:animate-out',
          'data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0',
          'data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95',
          'data-[side=bottom]:slide-in-from-top-2 data-[side=top]:slide-in-from-bottom-2',
        )"
      >
        <CalendarRoot
          v-slot="{ grid, weekDays }"
          :model-value="calendarValue"
          :disabled="disabled"
          class="p-3"
          @update:model-value="onSelect"
        >
          <CalendarHeader class="flex items-center justify-between">
            <CalendarPrev
              class="inline-flex size-7 items-center justify-center rounded-md border bg-transparent p-0 opacity-50 hover:opacity-100 disabled:pointer-events-none"
            >
              <ChevronLeft class="size-4" />
            </CalendarPrev>
            <CalendarHeading class="text-sm font-medium" />
            <CalendarNext
              class="inline-flex size-7 items-center justify-center rounded-md border bg-transparent p-0 opacity-50 hover:opacity-100 disabled:pointer-events-none"
            >
              <ChevronRight class="size-4" />
            </CalendarNext>
          </CalendarHeader>

          <div class="mt-2 flex flex-col space-y-4 sm:flex-row sm:space-x-4 sm:space-y-0">
            <CalendarGrid v-for="month in grid" :key="month.value.toString()">
              <CalendarGridHead>
                <CalendarGridRow class="flex">
                  <CalendarHeadCell
                    v-for="day in weekDays"
                    :key="day"
                    class="w-8 rounded-md text-[0.8rem] font-normal text-muted-foreground"
                  >
                    {{ day }}
                  </CalendarHeadCell>
                </CalendarGridRow>
              </CalendarGridHead>
              <CalendarGridBody>
                <CalendarGridRow
                  v-for="(weekDates, index) in month.rows"
                  :key="`week-${index}`"
                  class="mt-2 flex w-full"
                >
                  <CalendarCell
                    v-for="weekDate in weekDates"
                    :key="weekDate.toString()"
                    :date="weekDate"
                    class="relative p-0 text-center text-sm"
                  >
                    <CalendarCellTrigger
                      :day="weekDate"
                      :month="month.value"
                      :class="cn(
                        'inline-flex size-8 items-center justify-center rounded-md p-0 text-sm font-normal ring-offset-background transition-colors',
                        'hover:bg-accent hover:text-accent-foreground',
                        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2',
                        'data-[selected]:bg-primary data-[selected]:text-primary-foreground data-[selected]:hover:bg-primary data-[selected]:hover:text-primary-foreground',
                        'data-[today]:bg-accent data-[today]:text-accent-foreground',
                        'data-[outside-view]:text-muted-foreground data-[outside-view]:opacity-50',
                        'data-[disabled]:pointer-events-none data-[disabled]:opacity-50',
                      )"
                    />
                  </CalendarCell>
                </CalendarGridRow>
              </CalendarGridBody>
            </CalendarGrid>
          </div>
        </CalendarRoot>
      </PopoverContent>
    </PopoverPortal>
  </PopoverRoot>
</template>
