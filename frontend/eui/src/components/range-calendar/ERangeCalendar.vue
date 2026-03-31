<script setup lang="ts">
import { ChevronLeft, ChevronRight } from 'lucide-vue-next'
import {
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
} from 'reka-ui'
import { cn } from '@/utils/cn'
import { buttonVariants } from '@/components/button/types'
import type { ERangeCalendarProps, ERangeCalendarEmits } from './types'

const props = defineProps<ERangeCalendarProps>()
const emit = defineEmits<ERangeCalendarEmits>()
</script>

<template>
  <RangeCalendarRoot
    v-slot="{ grid, weekDays }"
    data-slot="range-calendar"
    :model-value="props.modelValue as any"
    :default-value="props.defaultValue as any"
    :disabled="props.disabled"
    :readonly="props.readonly"
    :locale="props.locale"
    :min-value="props.minValue"
    :max-value="props.maxValue"
    :class="cn('p-3', props.class)"
    @update:model-value="emit('update:modelValue', $event)"
  >
    <RangeCalendarHeader class="flex justify-center pt-1 relative items-center w-full px-8">
      <RangeCalendarPrev
        :class="cn(
          buttonVariants({ variant: 'outline' }),
          'absolute left-1 size-7 bg-transparent p-0 opacity-50 hover:opacity-100',
        )"
      >
        <ChevronLeft class="size-4" />
      </RangeCalendarPrev>
      <RangeCalendarHeading class="text-sm font-medium" />
      <RangeCalendarNext
        :class="cn(
          buttonVariants({ variant: 'outline' }),
          'absolute right-1 size-7 bg-transparent p-0 opacity-50 hover:opacity-100',
        )"
      >
        <ChevronRight class="size-4" />
      </RangeCalendarNext>
    </RangeCalendarHeader>

    <div class="flex flex-col gap-y-4 mt-4 sm:flex-row sm:gap-x-4 sm:gap-y-0">
      <RangeCalendarGrid v-for="month in grid" :key="month.value.toString()" class="w-full border-collapse space-x-1">
        <RangeCalendarGridHead>
          <RangeCalendarGridRow class="flex">
            <RangeCalendarHeadCell
              v-for="day in weekDays"
              :key="day"
              class="text-muted-foreground rounded-md flex-1 font-normal text-[0.8rem]"
            >
              {{ day }}
            </RangeCalendarHeadCell>
          </RangeCalendarGridRow>
        </RangeCalendarGridHead>
        <RangeCalendarGridBody>
          <RangeCalendarGridRow
            v-for="(weekDates, index) in month.rows"
            :key="`weekDate-${index}`"
            class="flex mt-2 w-full"
          >
            <RangeCalendarCell
              v-for="weekDate in weekDates"
              :key="weekDate.toString()"
              :date="weekDate"
              class="relative p-0 text-center text-sm focus-within:relative focus-within:z-20 [&:has([data-selected])]:bg-accent first:[&:has([data-selected])]:rounded-l-md last:[&:has([data-selected])]:rounded-r-md [&:has([data-selected][data-selection-end])]:rounded-r-md [&:has([data-selected][data-selection-start])]:rounded-l-md"
            >
              <RangeCalendarCellTrigger
                :day="weekDate"
                :month="month.value"
                :class="cn(
                  buttonVariants({ variant: 'ghost' }),
                  'h-8 w-8 p-0 font-normal data-[selected]:opacity-100',
                  '[&[data-today]:not([data-selected])]:bg-accent [&[data-today]:not([data-selected])]:text-accent-foreground',
                  'data-[selection-start]:bg-primary data-[selection-start]:text-primary-foreground data-[selection-start]:hover:bg-primary data-[selection-start]:hover:text-primary-foreground',
                  'data-[selection-end]:bg-primary data-[selection-end]:text-primary-foreground data-[selection-end]:hover:bg-primary data-[selection-end]:hover:text-primary-foreground',
                  'data-[outside-view]:text-muted-foreground',
                  'data-[disabled]:text-muted-foreground data-[disabled]:opacity-50',
                  'data-[unavailable]:text-destructive-foreground data-[unavailable]:line-through',
                )"
              />
            </RangeCalendarCell>
          </RangeCalendarGridRow>
        </RangeCalendarGridBody>
      </RangeCalendarGrid>
    </div>
  </RangeCalendarRoot>
</template>
