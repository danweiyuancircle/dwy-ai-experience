<script setup lang="ts">
import { ref, computed } from 'vue'
import { ChevronRight, ChevronLeft } from 'lucide-vue-next'
import { cn } from '@/utils/cn'
import type { ETransferProps, ETransferEmits, TransferItem } from './types'

const props = withDefaults(defineProps<ETransferProps>(), {
  modelValue: () => [],
  data: () => [],
  filterable: false,
  titles: () => ['Source', 'Target'],
})

const emit = defineEmits<ETransferEmits>()

const leftFilter = ref('')
const rightFilter = ref('')
const leftChecked = ref<Set<string | number>>(new Set())
const rightChecked = ref<Set<string | number>>(new Set())

const selectedValues = computed(() => new Set(props.modelValue))

const leftItems = computed(() =>
  props.data.filter(item => !selectedValues.value.has(item.value))
)

const rightItems = computed(() =>
  props.data.filter(item => selectedValues.value.has(item.value))
)

const filteredLeft = computed(() =>
  leftFilter.value
    ? leftItems.value.filter(i => i.label.toLowerCase().includes(leftFilter.value.toLowerCase()))
    : leftItems.value
)

const filteredRight = computed(() =>
  rightFilter.value
    ? rightItems.value.filter(i => i.label.toLowerCase().includes(rightFilter.value.toLowerCase()))
    : rightItems.value
)

function moveRight() {
  const moved = [...leftChecked.value]
  const newValue = [...(props.modelValue ?? []), ...moved]
  emit('update:modelValue', newValue)
  emit('change', newValue, 'right', moved)
  leftChecked.value = new Set()
}

function moveLeft() {
  const moved = [...rightChecked.value]
  const newValue = (props.modelValue ?? []).filter(v => !rightChecked.value.has(v))
  emit('update:modelValue', newValue)
  emit('change', newValue, 'left', moved)
  rightChecked.value = new Set()
}

function toggleLeft(value: string | number) {
  if (leftChecked.value.has(value)) leftChecked.value.delete(value)
  else leftChecked.value.add(value)
}

function toggleRight(value: string | number) {
  if (rightChecked.value.has(value)) rightChecked.value.delete(value)
  else rightChecked.value.add(value)
}

function toggleAllLeft(checked: boolean) {
  if (checked) filteredLeft.value.filter(i => !i.disabled).forEach(i => leftChecked.value.add(i.value))
  else leftChecked.value = new Set()
}

function toggleAllRight(checked: boolean) {
  if (checked) filteredRight.value.filter(i => !i.disabled).forEach(i => rightChecked.value.add(i.value))
  else rightChecked.value = new Set()
}

const allLeftChecked = computed(() =>
  filteredLeft.value.length > 0 &&
  filteredLeft.value.filter(i => !i.disabled).every(i => leftChecked.value.has(i.value))
)

const allRightChecked = computed(() =>
  filteredRight.value.length > 0 &&
  filteredRight.value.filter(i => !i.disabled).every(i => rightChecked.value.has(i.value))
)
</script>

<template>
  <div :class="cn('flex items-stretch gap-3', props.class)">
    <!-- Left panel -->
    <div class="flex flex-col rounded-md border min-w-[180px] flex-1">
      <div class="flex items-center gap-2 border-b px-3 py-2">
        <input
          type="checkbox"
          :checked="allLeftChecked"
          :indeterminate="leftChecked.size > 0 && !allLeftChecked"
          class="rounded border-input"
          @change="toggleAllLeft(($event.target as HTMLInputElement).checked)"
        />
        <span class="text-sm font-medium flex-1">{{ props.titles[0] }}</span>
        <span class="text-xs text-muted-foreground">{{ leftChecked.size }}/{{ filteredLeft.length }}</span>
      </div>
      <div v-if="props.filterable" class="px-3 py-2 border-b">
        <input
          v-model="leftFilter"
          type="text"
          placeholder="Filter..."
          class="w-full h-7 rounded border border-input bg-transparent px-2 text-sm outline-none"
        />
      </div>
      <ul class="flex-1 overflow-y-auto p-1 min-h-[120px]">
        <li
          v-for="item in filteredLeft"
          :key="item.value"
          :class="cn(
            'flex items-center gap-2 rounded-sm px-2 py-1.5 text-sm cursor-default select-none',
            item.disabled ? 'opacity-50 pointer-events-none' : 'hover:bg-accent',
            leftChecked.has(item.value) ? 'bg-accent/50' : '',
          )"
          @click="!item.disabled && toggleLeft(item.value)"
        >
          <input
            type="checkbox"
            :checked="leftChecked.has(item.value)"
            :disabled="item.disabled"
            class="rounded border-input"
            @change.stop="toggleLeft(item.value)"
          />
          {{ item.label }}
        </li>
      </ul>
    </div>

    <!-- Buttons -->
    <div class="flex flex-col items-center justify-center gap-2">
      <button
        :disabled="leftChecked.size === 0"
        class="flex items-center justify-center size-8 rounded-md border border-input bg-background shadow-xs hover:bg-accent disabled:opacity-50 disabled:cursor-not-allowed"
        @click="moveRight"
      >
        <ChevronRight class="size-4" />
      </button>
      <button
        :disabled="rightChecked.size === 0"
        class="flex items-center justify-center size-8 rounded-md border border-input bg-background shadow-xs hover:bg-accent disabled:opacity-50 disabled:cursor-not-allowed"
        @click="moveLeft"
      >
        <ChevronLeft class="size-4" />
      </button>
    </div>

    <!-- Right panel -->
    <div class="flex flex-col rounded-md border min-w-[180px] flex-1">
      <div class="flex items-center gap-2 border-b px-3 py-2">
        <input
          type="checkbox"
          :checked="allRightChecked"
          :indeterminate="rightChecked.size > 0 && !allRightChecked"
          class="rounded border-input"
          @change="toggleAllRight(($event.target as HTMLInputElement).checked)"
        />
        <span class="text-sm font-medium flex-1">{{ props.titles[1] }}</span>
        <span class="text-xs text-muted-foreground">{{ rightChecked.size }}/{{ filteredRight.length }}</span>
      </div>
      <div v-if="props.filterable" class="px-3 py-2 border-b">
        <input
          v-model="rightFilter"
          type="text"
          placeholder="Filter..."
          class="w-full h-7 rounded border border-input bg-transparent px-2 text-sm outline-none"
        />
      </div>
      <ul class="flex-1 overflow-y-auto p-1 min-h-[120px]">
        <li
          v-for="item in filteredRight"
          :key="item.value"
          :class="cn(
            'flex items-center gap-2 rounded-sm px-2 py-1.5 text-sm cursor-default select-none',
            item.disabled ? 'opacity-50 pointer-events-none' : 'hover:bg-accent',
            rightChecked.has(item.value) ? 'bg-accent/50' : '',
          )"
          @click="!item.disabled && toggleRight(item.value)"
        >
          <input
            type="checkbox"
            :checked="rightChecked.has(item.value)"
            :disabled="item.disabled"
            class="rounded border-input"
            @change.stop="toggleRight(item.value)"
          />
          {{ item.label }}
        </li>
      </ul>
    </div>
  </div>
</template>
