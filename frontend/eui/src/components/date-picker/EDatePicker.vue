<!--
  EDatePicker 日期选择器组件
  基于 reka-ui 的 Calendar / RangeCalendar / MonthPicker / YearPicker 原语封装
  通过 type 切换单日 / 区间 / 月 / 年四种模式，值统一以字符串形式对外交互
-->
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
  RangeCalendarRoot,
  RangeCalendarHeader,
  RangeCalendarHeading,
  RangeCalendarPrev,
  RangeCalendarNext,
  RangeCalendarGrid,
  RangeCalendarGridHead,
  RangeCalendarGridRow,
  RangeCalendarHeadCell,
  RangeCalendarGridBody,
  RangeCalendarCell,
  RangeCalendarCellTrigger,
  MonthPickerRoot,
  MonthPickerHeader,
  MonthPickerHeading,
  MonthPickerPrev,
  MonthPickerNext,
  MonthPickerGrid,
  MonthPickerGridBody,
  MonthPickerGridRow,
  MonthPickerCell,
  MonthPickerCellTrigger,
  YearPickerRoot,
  YearPickerHeader,
  YearPickerHeading,
  YearPickerPrev,
  YearPickerNext,
  YearPickerGrid,
  YearPickerGridBody,
  YearPickerGridRow,
  YearPickerCell,
  YearPickerCellTrigger,
  PopoverAnchor,
  PopoverContent,
  PopoverPortal,
  PopoverRoot,
  PopoverTrigger,
} from 'reka-ui'
import { CalendarDate } from '@internationalized/date'
import type { DateValue } from '@internationalized/date'
import { cn } from '@/utils/cn'
import type { EDatePickerProps, EDatePickerEmits } from './types'

const props = withDefaults(defineProps<EDatePickerProps>(), {
  type: 'date',
  placeholder: 'Pick a date',
  startPlaceholder: 'Start date',
  endPlaceholder: 'End date',
  rangeSeparator: '至',
  disabled: false,
  clearable: false,
  format: 'YYYY-MM-DD',
})

const emit = defineEmits<EDatePickerEmits>()

const open = ref(false)

// --- 辅助函数 ---

/** 将原生 Date 转换为 reka-ui 需要的 CalendarDate */
function toCalendarDate(d: Date): CalendarDate {
  return new CalendarDate(d.getFullYear(), d.getMonth() + 1, d.getDate())
}

/** 尝试将字符串或 Date 解析为 CalendarDate，失败返回 undefined */
function parseToCalendarDate(val: string | Date | undefined): CalendarDate | undefined {
  if (!val) return undefined
  try {
    const d = val instanceof Date ? val : new Date(val)
    if (isNaN(d.getTime())) return undefined
    return toCalendarDate(d)
  } catch {
    return undefined
  }
}

/** CalendarDate 反向转换为原生 Date */
function calendarDateToDate(cd: CalendarDate): Date {
  return new Date(cd.year, cd.month - 1, cd.day)
}

/** 根据 format（支持 YYYY / MM / DD）格式化 CalendarDate 为字符串 */
function formatCalendarDate(date: CalendarDate, fmt?: string): string {
  const f = fmt ?? props.format
  const y = String(date.year)
  const m = String(date.month).padStart(2, '0')
  const d = String(date.day).padStart(2, '0')
  return f.replace('YYYY', y).replace('MM', m).replace('DD', d)
}

/** 将 disabledDate prop 包装为 reka-ui Calendar 的 isDateUnavailable 形式 */
function isDateUnavailable(date: DateValue): boolean {
  if (!props.disabledDate) return false
  const jsDate = new Date(date.year, date.month - 1, date.day)
  return props.disabledDate(jsDate)
}

// --- 各类型的显示格式计算 ---
const effectiveFormat = computed(() => {
  if (props.type === 'month') return 'YYYY-MM'
  if (props.type === 'year') return 'YYYY'
  return props.format
})

// --- 单日模式 ---

const calendarValue = computed(() => {
  if (props.type !== 'date') return undefined
  if (!props.modelValue || Array.isArray(props.modelValue)) return undefined
  return parseToCalendarDate(props.modelValue as string | Date)
})

const displayValue = computed(() => {
  if (props.type === 'date') {
    if (!calendarValue.value) return ''
    return formatCalendarDate(calendarValue.value, effectiveFormat.value)
  }
  if (props.type === 'daterange') {
    return rangeDisplayValue.value
  }
  if (props.type === 'month') {
    return monthDisplayValue.value
  }
  if (props.type === 'year') {
    return yearDisplayValue.value
  }
  return ''
})

/** 单日模式选中：格式化为字符串后派发并关闭面板 */
function onSelectDate(val: any) {
  if (!val) return
  const cd = val as CalendarDate
  const str = formatCalendarDate(cd, effectiveFormat.value)
  emit('update:modelValue', str)
  emit('change', str)
  open.value = false
}

// --- 区间模式 ---

const rangeCalendarValue = computed(() => {
  if (props.type !== 'daterange') return undefined
  if (!props.modelValue || !Array.isArray(props.modelValue)) return undefined
  const [startVal, endVal] = props.modelValue as [string | Date, string | Date]
  const startCd = parseToCalendarDate(startVal)
  const endCd = parseToCalendarDate(endVal)
  if (!startCd || !endCd) return undefined
  return { start: startCd, end: endCd }
})

const rangeDisplayValue = computed(() => {
  if (!rangeCalendarValue.value) return ''
  const startStr = formatCalendarDate(rangeCalendarValue.value.start, effectiveFormat.value)
  const endStr = formatCalendarDate(rangeCalendarValue.value.end, effectiveFormat.value)
  return `${startStr} ${props.rangeSeparator} ${endStr}`
})

/** 区间模式选中：起止都就绪时才派发并关闭 */
function onSelectRange(val: any) {
  if (!val || !val.start || !val.end) return
  const startStr = formatCalendarDate(val.start as CalendarDate, effectiveFormat.value)
  const endStr = formatCalendarDate(val.end as CalendarDate, effectiveFormat.value)
  emit('update:modelValue', [startStr, endStr])
  emit('change', [startStr, endStr])
  open.value = false
}

// --- 月模式 ---

const monthCalendarValue = computed(() => {
  if (props.type !== 'month') return undefined
  if (!props.modelValue || Array.isArray(props.modelValue)) return undefined
  const val = props.modelValue as string | Date
  try {
    const d = val instanceof Date ? val : new Date(val + (typeof val === 'string' && val.length <= 7 ? '-01' : ''))
    if (isNaN(d.getTime())) return undefined
    return new CalendarDate(d.getFullYear(), d.getMonth() + 1, 1)
  } catch {
    return undefined
  }
})

const monthDisplayValue = computed(() => {
  if (!monthCalendarValue.value) return ''
  return formatCalendarDate(monthCalendarValue.value, 'YYYY-MM')
})

/** 月模式选中：按 YYYY-MM 格式化 */
function onSelectMonth(val: any) {
  if (!val) return
  const cd = val as CalendarDate
  const str = formatCalendarDate(cd, 'YYYY-MM')
  emit('update:modelValue', str)
  emit('change', str)
  open.value = false
}

/** 将 disabledDate 包装为 MonthPicker 的 isMonthUnavailable，取月首日做代理判定 */
function isMonthUnavailable(date: DateValue): boolean {
  if (!props.disabledDate) return false
  const jsDate = new Date(date.year, date.month - 1, 1)
  return props.disabledDate(jsDate)
}

// --- 年模式 ---

const yearCalendarValue = computed(() => {
  if (props.type !== 'year') return undefined
  if (!props.modelValue || Array.isArray(props.modelValue)) return undefined
  const val = props.modelValue as string | Date
  try {
    const d = val instanceof Date ? val : new Date(typeof val === 'string' && val.length === 4 ? `${val}-01-01` : val)
    if (isNaN(d.getTime())) return undefined
    return new CalendarDate(d.getFullYear(), 1, 1)
  } catch {
    return undefined
  }
})

const yearDisplayValue = computed(() => {
  if (!yearCalendarValue.value) return ''
  return formatCalendarDate(yearCalendarValue.value, 'YYYY')
})

/** 年模式选中：按 YYYY 格式化 */
function onSelectYear(val: any) {
  if (!val) return
  const cd = val as CalendarDate
  const str = formatCalendarDate(cd, 'YYYY')
  emit('update:modelValue', str)
  emit('change', str)
  open.value = false
}

/** 将 disabledDate 包装为 YearPicker 的 isYearUnavailable，取年首日做代理判定 */
function isYearUnavailable(date: DateValue): boolean {
  if (!props.disabledDate) return false
  const jsDate = new Date(date.year, 0, 1)
  return props.disabledDate(jsDate)
}

// --- 快捷选项 ---

/**
 * 快捷选项点击处理：根据当前 type 与 shortcut.value 派发对应格式的值
 */
function onShortcutClick(shortcut: { text: string; value: Date | Date[] | (() => Date | Date[]) }) {
  const resolved = typeof shortcut.value === 'function' ? shortcut.value() : shortcut.value

  if (props.type === 'daterange' && Array.isArray(resolved)) {
    const [start, end] = resolved
    const startStr = formatCalendarDate(toCalendarDate(start), effectiveFormat.value)
    const endStr = formatCalendarDate(toCalendarDate(end), effectiveFormat.value)
    emit('update:modelValue', [startStr, endStr])
    emit('change', [startStr, endStr])
  } else if (!Array.isArray(resolved)) {
    const cd = toCalendarDate(resolved)
    if (props.type === 'month') {
      const str = formatCalendarDate(cd, 'YYYY-MM')
      emit('update:modelValue', str)
      emit('change', str)
    } else if (props.type === 'year') {
      const str = formatCalendarDate(cd, 'YYYY')
      emit('update:modelValue', str)
      emit('change', str)
    } else {
      const str = formatCalendarDate(cd, effectiveFormat.value)
      emit('update:modelValue', str)
      emit('change', str)
    }
  }
  open.value = false
}

// --- 清空 ---

/** 点击清空按钮：派发 undefined 重置 modelValue */
function onClear(e: MouseEvent) {
  e.stopPropagation()
  emit('update:modelValue', undefined)
  emit('change', undefined)
}

const hasValue = computed(() => {
  if (!props.modelValue) return false
  if (Array.isArray(props.modelValue)) return props.modelValue.length === 2
  return !!props.modelValue
})

const triggerPlaceholder = computed(() => {
  if (props.type === 'daterange') {
    return `${props.startPlaceholder} ${props.rangeSeparator} ${props.endPlaceholder}`
  }
  return props.placeholder
})

const hasShortcuts = computed(() => props.shortcuts && props.shortcuts.length > 0)
</script>

<template>
  <PopoverRoot v-model:open="open">
    <PopoverAnchor as-child>
      <PopoverTrigger as-child>
        <button
          :disabled="disabled"
          :class="cn(
            'flex h-9 w-full items-center justify-between rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-xs transition-[color,box-shadow]',
            'outline-none focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px]',
            'disabled:cursor-not-allowed disabled:opacity-50',
            !hasValue && 'text-muted-foreground',
            type === 'daterange' && 'min-w-[280px]',
            props.class,
          )"
        >
          <span class="flex items-center gap-2">
            <CalendarDays class="size-4 shrink-0 opacity-50" />
            {{ displayValue || triggerPlaceholder }}
          </span>
          <X
            v-if="clearable && hasValue"
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
        <div :class="cn('flex', hasShortcuts && 'flex-row')">
          <!-- Shortcuts panel -->
          <div
            v-if="hasShortcuts"
            class="flex flex-col gap-1 border-r p-2 min-w-[100px]"
          >
            <button
              v-for="shortcut in shortcuts"
              :key="shortcut.text"
              class="rounded-md px-3 py-1.5 text-left text-sm hover:bg-accent hover:text-accent-foreground transition-colors"
              @click="onShortcutClick(shortcut)"
            >
              {{ shortcut.text }}
            </button>
          </div>

          <!-- Date picker (default) -->
          <CalendarRoot
            v-if="type === 'date'"
            v-slot="{ grid, weekDays }"
            :model-value="calendarValue"
            :disabled="disabled"
            :is-date-unavailable="disabledDate ? isDateUnavailable : undefined"
            class="p-3"
            @update:model-value="onSelectDate"
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
                          'inline-flex size-8 items-center justify-center rounded-md p-0 text-sm font-normal transition-colors',
                          'hover:bg-accent hover:text-accent-foreground',
                          'focus-visible:outline-none focus-visible:ring-ring/50 focus-visible:ring-[3px]',
                          'data-[selected]:bg-primary data-[selected]:text-primary-foreground data-[selected]:hover:bg-primary data-[selected]:hover:text-primary-foreground',
                          'data-[today]:bg-accent data-[today]:text-accent-foreground',
                          'data-[outside-view]:text-muted-foreground data-[outside-view]:opacity-50',
                          'data-[disabled]:pointer-events-none data-[disabled]:opacity-50',
                          'data-[unavailable]:pointer-events-none data-[unavailable]:text-muted-foreground data-[unavailable]:line-through data-[unavailable]:opacity-50',
                        )"
                      />
                    </CalendarCell>
                  </CalendarGridRow>
                </CalendarGridBody>
              </CalendarGrid>
            </div>
          </CalendarRoot>

          <!-- Date range picker -->
          <RangeCalendarRoot
            v-else-if="type === 'daterange'"
            v-slot="{ grid, weekDays }"
            :model-value="rangeCalendarValue as any"
            :disabled="disabled"
            :number-of-months="2"
            :is-date-unavailable="disabledDate ? isDateUnavailable : undefined"
            class="p-3"
            @update:model-value="onSelectRange"
          >
            <RangeCalendarHeader class="flex justify-center pt-1 relative items-center w-full px-8">
              <RangeCalendarPrev
                class="inline-flex size-7 items-center justify-center rounded-md border bg-transparent p-0 opacity-50 hover:opacity-100 absolute left-1 disabled:pointer-events-none"
              >
                <ChevronLeft class="size-4" />
              </RangeCalendarPrev>
              <RangeCalendarHeading class="text-sm font-medium" />
              <RangeCalendarNext
                class="inline-flex size-7 items-center justify-center rounded-md border bg-transparent p-0 opacity-50 hover:opacity-100 absolute right-1 disabled:pointer-events-none"
              >
                <ChevronRight class="size-4" />
              </RangeCalendarNext>
            </RangeCalendarHeader>

            <div class="flex flex-col gap-y-4 mt-2 sm:flex-row sm:gap-x-4 sm:gap-y-0">
              <RangeCalendarGrid v-for="month in grid" :key="month.value.toString()">
                <RangeCalendarGridHead>
                  <RangeCalendarGridRow class="flex">
                    <RangeCalendarHeadCell
                      v-for="day in weekDays"
                      :key="day"
                      class="w-8 rounded-md text-[0.8rem] font-normal text-muted-foreground"
                    >
                      {{ day }}
                    </RangeCalendarHeadCell>
                  </RangeCalendarGridRow>
                </RangeCalendarGridHead>
                <RangeCalendarGridBody>
                  <RangeCalendarGridRow
                    v-for="(weekDates, index) in month.rows"
                    :key="`week-${index}`"
                    class="mt-2 flex w-full"
                  >
                    <RangeCalendarCell
                      v-for="weekDate in weekDates"
                      :key="weekDate.toString()"
                      :date="weekDate"
                      :class="cn(
                        'relative p-0 text-center text-sm',
                        'focus-within:relative focus-within:z-20',
                        '[&:has([data-selected])]:bg-accent',
                        'first:[&:has([data-selected])]:rounded-l-md last:[&:has([data-selected])]:rounded-r-md',
                        '[&:has([data-selected][data-selection-end])]:rounded-r-md',
                        '[&:has([data-selected][data-selection-start])]:rounded-l-md',
                      )"
                    >
                      <RangeCalendarCellTrigger
                        :day="weekDate"
                        :month="month.value"
                        :class="cn(
                          'inline-flex size-8 items-center justify-center rounded-md p-0 text-sm font-normal transition-colors',
                          'hover:bg-accent hover:text-accent-foreground',
                          'focus-visible:outline-none focus-visible:ring-ring/50 focus-visible:ring-[3px]',
                          'data-[selected]:opacity-100',
                          'data-[selection-start]:bg-primary data-[selection-start]:text-primary-foreground data-[selection-start]:hover:bg-primary',
                          'data-[selection-end]:bg-primary data-[selection-end]:text-primary-foreground data-[selection-end]:hover:bg-primary',
                          '[&[data-today]:not([data-selected])]:bg-accent [&[data-today]:not([data-selected])]:text-accent-foreground',
                          'data-[outside-view]:text-muted-foreground data-[outside-view]:opacity-50',
                          'data-[disabled]:pointer-events-none data-[disabled]:opacity-50',
                          'data-[unavailable]:pointer-events-none data-[unavailable]:text-muted-foreground data-[unavailable]:line-through data-[unavailable]:opacity-50',
                        )"
                      />
                    </RangeCalendarCell>
                  </RangeCalendarGridRow>
                </RangeCalendarGridBody>
              </RangeCalendarGrid>
            </div>
          </RangeCalendarRoot>

          <!-- Month picker -->
          <MonthPickerRoot
            v-else-if="type === 'month'"
            v-slot="{ grid }"
            :model-value="monthCalendarValue"
            :disabled="disabled"
            :is-month-unavailable="disabledDate ? isMonthUnavailable : undefined"
            class="p-3"
            @update:model-value="onSelectMonth"
          >
            <MonthPickerHeader class="flex items-center justify-between px-8 relative">
              <MonthPickerPrev
                class="inline-flex size-7 items-center justify-center rounded-md border bg-transparent p-0 opacity-50 hover:opacity-100 absolute left-1 disabled:pointer-events-none"
              >
                <ChevronLeft class="size-4" />
              </MonthPickerPrev>
              <MonthPickerHeading class="text-sm font-medium" />
              <MonthPickerNext
                class="inline-flex size-7 items-center justify-center rounded-md border bg-transparent p-0 opacity-50 hover:opacity-100 absolute right-1 disabled:pointer-events-none"
              >
                <ChevronRight class="size-4" />
              </MonthPickerNext>
            </MonthPickerHeader>

            <MonthPickerGrid class="mt-2 w-full">
              <MonthPickerGridBody>
                <MonthPickerGridRow
                  v-for="(row, rowIndex) in grid.rows"
                  :key="`month-row-${rowIndex}`"
                  class="flex w-full justify-center gap-1 mt-1"
                >
                  <MonthPickerCell
                    v-for="monthItem in row"
                    :key="monthItem.toString()"
                    :date="monthItem"
                    class="relative p-0 text-center"
                  >
                    <MonthPickerCellTrigger
                      :month="monthItem"
                      :class="cn(
                        'inline-flex h-8 w-16 items-center justify-center rounded-md text-sm font-normal transition-colors',
                        'hover:bg-accent hover:text-accent-foreground',
                        'focus-visible:outline-none focus-visible:ring-ring/50 focus-visible:ring-[3px]',
                        'data-[selected]:bg-primary data-[selected]:text-primary-foreground',
                        'data-[disabled]:pointer-events-none data-[disabled]:opacity-50',
                        'data-[unavailable]:pointer-events-none data-[unavailable]:text-muted-foreground data-[unavailable]:line-through data-[unavailable]:opacity-50',
                      )"
                    />
                  </MonthPickerCell>
                </MonthPickerGridRow>
              </MonthPickerGridBody>
            </MonthPickerGrid>
          </MonthPickerRoot>

          <!-- Year picker -->
          <YearPickerRoot
            v-else-if="type === 'year'"
            v-slot="{ grid }"
            :model-value="yearCalendarValue"
            :disabled="disabled"
            :is-year-unavailable="disabledDate ? isYearUnavailable : undefined"
            class="p-3"
            @update:model-value="onSelectYear"
          >
            <YearPickerHeader class="flex items-center justify-between px-8 relative">
              <YearPickerPrev
                class="inline-flex size-7 items-center justify-center rounded-md border bg-transparent p-0 opacity-50 hover:opacity-100 absolute left-1 disabled:pointer-events-none"
              >
                <ChevronLeft class="size-4" />
              </YearPickerPrev>
              <YearPickerHeading class="text-sm font-medium" />
              <YearPickerNext
                class="inline-flex size-7 items-center justify-center rounded-md border bg-transparent p-0 opacity-50 hover:opacity-100 absolute right-1 disabled:pointer-events-none"
              >
                <ChevronRight class="size-4" />
              </YearPickerNext>
            </YearPickerHeader>

            <YearPickerGrid class="mt-2 w-full">
              <YearPickerGridBody>
                <YearPickerGridRow
                  v-for="(row, rowIndex) in grid.rows"
                  :key="`year-row-${rowIndex}`"
                  class="flex w-full justify-center gap-1 mt-1"
                >
                  <YearPickerCell
                    v-for="yearItem in row"
                    :key="yearItem.toString()"
                    :date="yearItem"
                    class="relative p-0 text-center"
                  >
                    <YearPickerCellTrigger
                      :year="yearItem"
                      :class="cn(
                        'inline-flex h-8 w-16 items-center justify-center rounded-md text-sm font-normal transition-colors',
                        'hover:bg-accent hover:text-accent-foreground',
                        'focus-visible:outline-none focus-visible:ring-ring/50 focus-visible:ring-[3px]',
                        'data-[selected]:bg-primary data-[selected]:text-primary-foreground',
                        'data-[disabled]:pointer-events-none data-[disabled]:opacity-50',
                        'data-[unavailable]:pointer-events-none data-[unavailable]:text-muted-foreground data-[unavailable]:line-through data-[unavailable]:opacity-50',
                      )"
                    />
                  </YearPickerCell>
                </YearPickerGridRow>
              </YearPickerGridBody>
            </YearPickerGrid>
          </YearPickerRoot>
        </div>
      </PopoverContent>
    </PopoverPortal>
  </PopoverRoot>
</template>
