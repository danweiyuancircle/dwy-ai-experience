<script setup lang="ts">
import { computed, ref } from 'vue'
import { ChevronDown, ChevronRight, X } from 'lucide-vue-next'
import { PopoverContent, PopoverPortal, PopoverRoot, PopoverTrigger } from 'reka-ui'
import { cn } from '@/utils/cn'
import type { ECascaderProps, ECascaderEmits, CascaderOption } from './types'

const props = withDefaults(defineProps<ECascaderProps>(), {
  options: () => [],
  placeholder: 'Select...',
  disabled: false,
  clearable: false,
  filterable: false,
})

const emit = defineEmits<ECascaderEmits>()

const open = ref(false)
const searchQuery = ref('')

/** Active path of selected options per level */
const activePath = ref<CascaderOption[]>([])

/** Options for each visible column */
const columns = computed((): CascaderOption[][] => {
  const cols: CascaderOption[][] = [getFilteredRoots()]
  for (const option of activePath.value) {
    if (option.children?.length) {
      cols.push(option.children)
    }
  }
  return cols
})

function getFilteredRoots(): CascaderOption[] {
  if (!props.filterable || !searchQuery.value) return props.options
  return filterOptions(props.options, searchQuery.value)
}

function filterOptions(options: CascaderOption[], query: string): CascaderOption[] {
  return options.filter((o) => {
    const matchSelf = o.label.toLowerCase().includes(query.toLowerCase())
    const matchChildren = o.children ? filterOptions(o.children, query).length > 0 : false
    return matchSelf || matchChildren
  })
}

function isInPath(option: CascaderOption, level: number): boolean {
  return activePath.value[level]?.value === option.value
}

function isLeaf(option: CascaderOption): boolean {
  return !option.children?.length
}

function onOptionClick(option: CascaderOption, level: number) {
  if (option.disabled) return

  // Trim path to current level and add this option
  activePath.value = [...activePath.value.slice(0, level), option]

  if (isLeaf(option)) {
    const values = activePath.value.map((o) => o.value)
    emit('update:modelValue', values)
    emit('change', values)
    open.value = false
    searchQuery.value = ''
  }
}

/** Build display label from modelValue */
const displayLabel = computed(() => {
  if (!props.modelValue?.length) return ''
  let nodes = props.options
  const labels: string[] = []
  for (const val of props.modelValue) {
    const found = nodes.find((o) => o.value === val)
    if (!found) break
    labels.push(found.label)
    nodes = found.children ?? []
  }
  return labels.join(' / ')
})

function onClear(e: MouseEvent) {
  e.stopPropagation()
  activePath.value = []
  emit('update:modelValue', [])
  emit('change', [])
}

function onOpenChange(val: boolean) {
  open.value = val
  if (!val) {
    searchQuery.value = ''
  }
}
</script>

<template>
  <PopoverRoot :open="open" @update:open="onOpenChange">
    <PopoverTrigger as-child>
      <button
        :disabled="disabled"
        :class="cn(
          'flex h-9 w-full items-center justify-between rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-xs',
          'focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2',
          'disabled:cursor-not-allowed disabled:opacity-50',
          !displayLabel && 'text-muted-foreground',
          props.class,
        )"
      >
        <span class="flex-1 truncate text-left">{{ displayLabel || placeholder }}</span>
        <div class="flex items-center gap-1">
          <X
            v-if="clearable && displayLabel"
            class="size-4 opacity-50 hover:opacity-100"
            @click.stop="onClear"
          />
          <ChevronDown class="size-4 opacity-50" />
        </div>
      </button>
    </PopoverTrigger>

    <PopoverPortal>
      <PopoverContent
        :side-offset="4"
        align="start"
        :class="cn(
          'z-50 rounded-md border bg-popover text-popover-foreground shadow-md outline-none p-0',
          'data-[state=open]:animate-in data-[state=closed]:animate-out',
          'data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0',
          'data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95',
        )"
      >
        <!-- Search input -->
        <div v-if="filterable" class="border-b p-2">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search..."
            class="w-full rounded-sm bg-transparent text-sm outline-none placeholder:text-muted-foreground"
          />
        </div>

        <!-- Cascading columns -->
        <div class="flex">
          <div
            v-for="(colOptions, colIdx) in columns"
            :key="colIdx"
            class="max-h-[240px] min-w-[140px] overflow-y-auto border-r last:border-r-0"
          >
            <button
              v-for="option in colOptions"
              :key="String(option.value)"
              :disabled="option.disabled"
              :class="cn(
                'flex w-full items-center justify-between gap-2 px-3 py-1.5 text-sm',
                'hover:bg-accent hover:text-accent-foreground',
                'disabled:pointer-events-none disabled:opacity-50',
                isInPath(option, colIdx) && 'bg-accent text-accent-foreground font-medium',
              )"
              @click="onOptionClick(option, colIdx)"
            >
              <span class="truncate">{{ option.label }}</span>
              <ChevronRight v-if="!isLeaf(option)" class="size-3.5 shrink-0 opacity-50" />
            </button>
            <div v-if="colOptions.length === 0" class="px-3 py-4 text-center text-xs text-muted-foreground">
              No options
            </div>
          </div>
        </div>
      </PopoverContent>
    </PopoverPortal>
  </PopoverRoot>
</template>
