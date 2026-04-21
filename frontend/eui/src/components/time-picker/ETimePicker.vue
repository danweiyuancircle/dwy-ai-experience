<!--
  ETimePicker 时间选择器
  使用 reka-ui Popover 弹出选时面板，左右两列分别滚动选择小时/分钟
  通过 hourStep/minuteStep 控制颗粒度；打开时自动滚动到当前选中项
-->
<script setup lang="ts">
import { computed, nextTick, ref, watch } from 'vue'
import { Clock } from 'lucide-vue-next'
import { PopoverContent, PopoverPortal, PopoverRoot, PopoverTrigger } from 'reka-ui'
import { cn } from '@/utils/cn'
import { useConfigProvider } from '@/composables/useConfigProvider'
import type { ETimePickerProps, ETimePickerEmits } from './types'

const { locale } = useConfigProvider()

const props = withDefaults(defineProps<ETimePickerProps>(), {
  disabled: false,
  hourStep: 1,
  minuteStep: 1,
})

const emit = defineEmits<ETimePickerEmits>()

const open = ref(false)

/** 从 HH:mm 字符串解析出小时 */
const parsedHour = computed(() => {
  if (!props.modelValue) return 0
  const [h] = props.modelValue.split(':')
  return parseInt(h ?? '0', 10)
})

const parsedMinute = computed(() => {
  if (!props.modelValue) return 0
  const [, m] = props.modelValue.split(':')
  return parseInt(m ?? '0', 10)
})

const selectedHour = ref(parsedHour.value)
const selectedMinute = ref(parsedMinute.value)

watch(() => props.modelValue, () => {
  selectedHour.value = parsedHour.value
  selectedMinute.value = parsedMinute.value
})

const hours = computed(() => {
  const list: number[] = []
  for (let h = 0; h < 24; h += props.hourStep) list.push(h)
  return list
})

const minutes = computed(() => {
  const list: number[] = []
  for (let m = 0; m < 60; m += props.minuteStep) list.push(m)
  return list
})

const displayValue = computed(() => {
  if (!props.modelValue) return ''
  return props.modelValue
})

function pad(n: number) {
  return String(n).padStart(2, '0')
}

function selectHour(h: number) {
  selectedHour.value = h
  emitValue()
}

function selectMinute(m: number) {
  selectedMinute.value = m
  emitValue()
}

function emitValue() {
  const val = `${pad(selectedHour.value)}:${pad(selectedMinute.value)}`
  emit('update:modelValue', val)
  emit('change', val)
}

/** 面板打开时将当前选中项滚动到可视中央 */
const hourListRef = ref<HTMLElement | null>(null)
const minuteListRef = ref<HTMLElement | null>(null)

watch(open, async (isOpen) => {
  if (!isOpen) return
  await nextTick()
  scrollToActive(hourListRef.value, selectedHour.value)
  scrollToActive(minuteListRef.value, selectedMinute.value)
})

function scrollToActive(el: HTMLElement | null, value: number) {
  if (!el) return
  const active = el.querySelector(`[data-value="${value}"]`) as HTMLElement | null
  if (active) active.scrollIntoView({ block: 'center' })
}
</script>

<template>
  <PopoverRoot v-model:open="open">
    <PopoverTrigger as-child>
      <button
        :disabled="disabled"
        :class="cn(
          'flex h-9 w-full items-center gap-2 rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-xs ring-offset-background',
          'focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2',
          'disabled:cursor-not-allowed disabled:opacity-50',
          !displayValue && 'text-muted-foreground',
          props.class,
        )"
      >
        <Clock class="size-4 shrink-0 opacity-50" />
        {{ displayValue || placeholder || locale.timePickerPlaceholder }}
      </button>
    </PopoverTrigger>

    <PopoverPortal>
      <PopoverContent
        :side-offset="4"
        align="start"
        :class="cn(
          'z-50 rounded-md border bg-popover p-2 text-popover-foreground shadow-md outline-none',
          'data-[state=open]:animate-in data-[state=closed]:animate-out',
          'data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0',
          'data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95',
        )"
      >
        <div class="flex gap-2">
          <!-- Hours column -->
          <div class="flex flex-col items-center gap-1">
            <span class="text-xs font-medium text-muted-foreground pb-1">{{ locale.timePickerHour }}</span>
            <div
              ref="hourListRef"
              class="h-[180px] overflow-y-auto scroll-smooth no-scrollbar"
            >
              <button
                v-for="h in hours"
                :key="h"
                :data-value="h"
                :class="cn(
                  'flex w-10 items-center justify-center rounded px-2 py-1 text-sm transition-colors',
                  'hover:bg-accent hover:text-accent-foreground',
                  selectedHour === h ? 'bg-primary text-primary-foreground font-medium' : '',
                )"
                @click="selectHour(h)"
              >
                {{ pad(h) }}
              </button>
            </div>
          </div>

          <!-- Separator -->
          <div class="flex items-center pt-6 text-muted-foreground font-bold">:</div>

          <!-- Minutes column -->
          <div class="flex flex-col items-center gap-1">
            <span class="text-xs font-medium text-muted-foreground pb-1">{{ locale.timePickerMinute }}</span>
            <div
              ref="minuteListRef"
              class="h-[180px] overflow-y-auto scroll-smooth no-scrollbar"
            >
              <button
                v-for="m in minutes"
                :key="m"
                :data-value="m"
                :class="cn(
                  'flex w-10 items-center justify-center rounded px-2 py-1 text-sm transition-colors',
                  'hover:bg-accent hover:text-accent-foreground',
                  selectedMinute === m ? 'bg-primary text-primary-foreground font-medium' : '',
                )"
                @click="selectMinute(m)"
              >
                {{ pad(m) }}
              </button>
            </div>
          </div>
        </div>

        <!-- Confirm button -->
        <div class="mt-2 flex justify-end border-t pt-2">
          <button
            class="rounded-md bg-primary px-3 py-1 text-xs text-primary-foreground hover:bg-primary/90"
            @click="open = false"
          >
            {{ locale.confirm }}
          </button>
        </div>
      </PopoverContent>
    </PopoverPortal>
  </PopoverRoot>
</template>
