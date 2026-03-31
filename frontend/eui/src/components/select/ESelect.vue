<script setup lang="ts">
import { computed, ref, nextTick } from 'vue'
import { Check, ChevronDown, ChevronUp, X, Search } from 'lucide-vue-next'
import {
  SelectRoot,
  SelectTrigger,
  SelectValue,
  SelectPortal,
  SelectContent,
  SelectViewport,
  SelectItem,
  SelectItemIndicator,
  SelectItemText,
  SelectGroup,
  SelectLabel,
  SelectScrollUpButton,
  SelectScrollDownButton,
  SelectIcon,
} from 'reka-ui'
import { cn } from '@/utils/cn'
import type { Option, GroupedOption } from '@/types'
import type { ESelectProps, ESelectEmits } from './types'

const props = withDefaults(defineProps<ESelectProps>(), {
  options: () => [],
  disabled: false,
  clearable: false,
  valueKey: 'value',
  labelKey: 'label',
  filterable: false,
  multiple: false,
  collapseTags: false,
})

const emit = defineEmits<ESelectEmits>()

/** Search query for filterable mode */
const filterQuery = ref('')

/** Reference to the filter input element for auto-focus */
const filterInputRef = ref<HTMLInputElement | null>(null)

/** Check if options are grouped (contain an options array inside) */
const isGrouped = computed(() => {
  return (
    Array.isArray(props.options) &&
    props.options.length > 0 &&
    'options' in (props.options[0] as any)
  )
})

/** Flatten all options from grouped or flat structures */
const flatOptions = computed(() => {
  if (!props.options || props.options.length === 0) return []
  if (isGrouped.value) {
    return (props.options as GroupedOption[]).flatMap((g) => g.options)
  }
  return props.options as Option[]
})

/** Extract the value from an option using the configured valueKey */
function optionValue(option: Record<string, any>): string | number {
  return option[props.valueKey] as string | number
}

/** Extract the label from an option using the configured labelKey */
function optionLabel(option: Record<string, any>): string {
  return option[props.labelKey] as string
}

/** Check if an option label matches the current filter query (case-insensitive) */
function matchesFilter(option: Record<string, any>): boolean {
  if (!props.filterable || !filterQuery.value) return true
  return optionLabel(option).toLowerCase().includes(filterQuery.value.toLowerCase())
}

/** Grouped options cast to the correct type */
const groupedOptions = computed((): GroupedOption[] => {
  if (!isGrouped.value) return []
  return props.options as GroupedOption[]
})

/** Grouped options filtered by the search query */
const filteredGroupedOptions = computed((): GroupedOption[] => {
  if (!props.filterable || !filterQuery.value) return groupedOptions.value
  return groupedOptions.value
    .map((group) => ({
      ...group,
      options: group.options.filter(matchesFilter),
    }))
    .filter((group) => group.options.length > 0)
})

/** Flat options filtered by the search query */
const filteredFlatOptions = computed((): Option[] => {
  if (!props.filterable || !filterQuery.value) return flatOptions.value
  return flatOptions.value.filter(matchesFilter)
})

/** Whether the dropdown has any visible options after filtering */
const hasFilteredResults = computed(() => {
  if (isGrouped.value) {
    return filteredGroupedOptions.value.some((g) => g.options.length > 0)
  }
  return filteredFlatOptions.value.length > 0
})

const triggerSizeClass = computed(() => {
  if (props.size === 'sm') return 'text-xs'
  if (props.size === 'lg') return 'text-base'
  return 'text-sm'
})

/** Minimum height class for trigger based on size (used in multiple mode) */
const triggerMinHeightClass = computed(() => {
  if (props.size === 'sm') return 'min-h-8'
  if (props.size === 'lg') return 'min-h-10'
  return 'min-h-9'
})

/** Fixed height class for trigger (used in single mode) */
const triggerFixedHeightClass = computed(() => {
  if (props.size === 'sm') return 'h-8'
  if (props.size === 'lg') return 'h-10'
  return 'h-9'
})

// --- Single-select helpers ---

/** Convert modelValue to string for reka-ui SelectRoot in single mode */
const modelStr = computed(() => {
  if (props.multiple) return undefined
  if (props.modelValue === undefined) return undefined
  return String(props.modelValue)
})

/** Handle value update from reka-ui in single-select mode */
function onUpdate(value: string) {
  const found = flatOptions.value.find((o) => String(optionValue(o)) === value)
  const finalValue = found ? optionValue(found) : value
  emit('update:modelValue', finalValue)
  emit('change', finalValue)
}

// --- Multiple-select helpers ---

/** Convert modelValue array to string array for reka-ui SelectRoot in multiple mode */
const modelArray = computed(() => {
  if (!props.multiple) return []
  if (!Array.isArray(props.modelValue)) return []
  return props.modelValue.map(String)
})

/** Resolve selected values to their option objects for rendering tags */
const selectedOptions = computed((): Option[] => {
  if (!props.multiple || !Array.isArray(props.modelValue)) return []
  return props.modelValue
    .map((val) => flatOptions.value.find((o) => String(optionValue(o)) === String(val)))
    .filter((o): o is Option => o !== undefined)
})

/** Tags visible in the trigger (all tags or just the first, depending on collapseTags) */
const visibleTags = computed(() => {
  if (props.collapseTags) return selectedOptions.value.slice(0, 1)
  return selectedOptions.value
})

/** Number of hidden tags when collapseTags is active */
const hiddenTagCount = computed(() => {
  if (!props.collapseTags) return 0
  return Math.max(0, selectedOptions.value.length - 1)
})

/** Handle value update from reka-ui in multi-select mode */
function onUpdateMultiple(value: string[]) {
  const finalValues = value.map((v) => {
    const found = flatOptions.value.find((o) => String(optionValue(o)) === v)
    return found ? optionValue(found) : v
  })
  emit('update:modelValue', finalValues)
  emit('change', finalValues)
}

/** Remove a single tag by its value in multi-select mode */
function removeTag(event: MouseEvent, val: string | number) {
  event.stopPropagation()
  event.preventDefault()
  if (props.disabled) return
  const current = Array.isArray(props.modelValue) ? [...props.modelValue] : []
  const next = current.filter((v) => String(v) !== String(val))
  emit('update:modelValue', next)
  emit('change', next)
}

// --- Shared handlers ---

/** Handle dropdown open/close state changes */
function onOpenChange(open: boolean) {
  emit('visible-change', open)
  if (open && props.filterable) {
    nextTick(() => filterInputRef.value?.focus())
  }
  if (!open) {
    filterQuery.value = ''
  }
}

/** Handle click on the clear button (single mode) */
function onClear(event: MouseEvent) {
  event.stopPropagation()
  if (props.multiple) {
    emit('update:modelValue', [])
    emit('change', [])
  } else {
    emit('update:modelValue', undefined)
    emit('change', undefined)
  }
}

/** Whether the clear button should be shown */
const showClear = computed(() => {
  if (!props.clearable) return false
  if (props.multiple) {
    return Array.isArray(props.modelValue) && props.modelValue.length > 0
  }
  return props.modelValue !== undefined && props.modelValue !== ''
})

/** Prevent filter input keyboard events from propagating to SelectContent typeahead */
function onFilterKeydown(event: KeyboardEvent) {
  event.stopPropagation()
}

// Item class shared between flat and grouped option rendering
const itemClass = 'focus:bg-accent focus:text-accent-foreground [&_svg:not([class*=\'text-\'])]:text-muted-foreground relative flex w-full cursor-default items-center gap-2 rounded-sm py-1.5 pr-8 pl-2 text-sm outline-hidden select-none data-[disabled]:pointer-events-none data-[disabled]:opacity-50 [&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*=\'size-\'])]:size-4'
</script>

<template>
  <!-- Multiple mode -->
  <SelectRoot
    v-if="multiple"
    :model-value="modelArray"
    :disabled="disabled"
    multiple
    @update:model-value="onUpdateMultiple"
    @update:open="onOpenChange"
  >
    <SelectTrigger
      data-slot="select-trigger"
      :class="cn(
        'border-input data-[placeholder]:text-muted-foreground [&_svg:not([class*=\'text-\'])]:text-muted-foreground focus-visible:border-ring focus-visible:ring-ring/50 aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive dark:bg-input/30 dark:hover:bg-input/50 flex w-full items-center justify-between gap-2 rounded-md border bg-transparent px-3 py-1.5 whitespace-nowrap shadow-xs transition-[color,box-shadow] outline-none focus-visible:ring-[3px] disabled:cursor-not-allowed disabled:opacity-50 [&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*=\'size-\'])]:size-4',
        triggerSizeClass,
        triggerMinHeightClass,
        props.class,
      )"
    >
      <!-- Tags area -->
      <div class="flex flex-1 flex-wrap items-center gap-1 overflow-hidden">
        <template v-if="selectedOptions.length > 0">
          <span
            v-for="option in visibleTags"
            :key="optionValue(option)"
            :class="cn(
              'inline-flex items-center gap-1 rounded bg-secondary text-secondary-foreground px-1.5 py-0.5 text-xs font-medium max-w-[120px]',
            )"
          >
            <span class="truncate">{{ optionLabel(option) }}</span>
            <button
              type="button"
              tabindex="-1"
              class="flex shrink-0 items-center text-muted-foreground hover:text-foreground transition-colors pointer-events-auto"
              @click="removeTag($event, optionValue(option))"
              @pointerdown.stop
            >
              <X class="size-3" />
            </button>
          </span>
          <span
            v-if="hiddenTagCount > 0"
            class="inline-flex items-center rounded bg-muted text-muted-foreground px-1.5 py-0.5 text-xs font-medium"
          >
            +{{ hiddenTagCount }}
          </span>
        </template>
        <span v-else class="text-muted-foreground">{{ placeholder }}</span>
      </div>

      <button
        v-if="showClear"
        type="button"
        tabindex="-1"
        class="ml-auto flex items-center text-muted-foreground hover:text-foreground transition-colors pointer-events-auto"
        @click="onClear"
        @pointerdown.stop
      >
        <X class="size-4" />
      </button>
      <SelectIcon v-else as-child>
        <ChevronDown class="size-4 opacity-50 ml-auto" />
      </SelectIcon>
    </SelectTrigger>

    <SelectPortal>
      <SelectContent
        data-slot="select-content"
        position="popper"
        :class="cn(
          'bg-popover text-popover-foreground data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[side=bottom]:slide-in-from-top-2 data-[side=left]:slide-in-from-right-2 data-[side=right]:slide-in-from-left-2 data-[side=top]:slide-in-from-bottom-2 relative z-50 max-h-(--reka-select-content-available-height) min-w-[8rem] overflow-x-hidden overflow-y-auto rounded-md border shadow-md',
          'data-[side=bottom]:translate-y-1 data-[side=left]:-translate-x-1 data-[side=right]:translate-x-1 data-[side=top]:-translate-y-1',
        )"
      >
        <SelectScrollUpButton class="flex cursor-default items-center justify-center py-1">
          <ChevronUp class="size-4" />
        </SelectScrollUpButton>

        <!-- Filter input -->
        <div v-if="filterable" class="sticky top-0 z-10 bg-popover p-1.5 border-b">
          <div class="flex items-center gap-2 px-2 py-1 rounded-sm bg-muted/50">
            <Search class="size-4 shrink-0 text-muted-foreground" />
            <input
              ref="filterInputRef"
              v-model="filterQuery"
              type="text"
              class="flex-1 bg-transparent text-sm outline-none placeholder:text-muted-foreground"
              placeholder="Search..."
              @keydown="onFilterKeydown"
            />
          </div>
        </div>

        <SelectViewport class="p-1 h-[var(--reka-select-trigger-height)] w-full min-w-[var(--reka-select-trigger-width)] scroll-my-1">
          <!-- No results message -->
          <div
            v-if="filterable && !hasFilteredResults"
            class="py-6 text-center text-sm text-muted-foreground"
          >
            No options found.
          </div>

          <!-- Grouped options -->
          <template v-if="isGrouped">
            <SelectGroup
              v-for="(group, gi) in filteredGroupedOptions"
              :key="gi"
            >
              <SelectLabel class="text-muted-foreground px-2 py-1.5 text-xs">
                {{ group.label }}
              </SelectLabel>
              <SelectItem
                v-for="option in group.options"
                :key="optionValue(option)"
                :value="String(optionValue(option))"
                :disabled="option.disabled"
                :class="cn(itemClass)"
              >
                <span class="absolute right-2 flex size-3.5 items-center justify-center">
                  <SelectItemIndicator>
                    <Check class="size-4" />
                  </SelectItemIndicator>
                </span>
                <SelectItemText>{{ optionLabel(option) }}</SelectItemText>
              </SelectItem>
            </SelectGroup>
          </template>

          <!-- Flat options -->
          <template v-else>
            <SelectItem
              v-for="option in filteredFlatOptions"
              :key="optionValue(option)"
              :value="String(optionValue(option))"
              :disabled="option.disabled"
              :class="cn(itemClass)"
            >
              <span class="absolute right-2 flex size-3.5 items-center justify-center">
                <SelectItemIndicator>
                  <Check class="size-4" />
                </SelectItemIndicator>
              </span>
              <SelectItemText>{{ optionLabel(option) }}</SelectItemText>
            </SelectItem>
          </template>
        </SelectViewport>

        <SelectScrollDownButton class="flex cursor-default items-center justify-center py-1">
          <ChevronDown class="size-4" />
        </SelectScrollDownButton>
      </SelectContent>
    </SelectPortal>
  </SelectRoot>

  <!-- Single mode (original behavior) -->
  <SelectRoot
    v-else
    :model-value="modelStr"
    :disabled="disabled"
    @update:model-value="onUpdate"
    @update:open="onOpenChange"
  >
    <SelectTrigger
      data-slot="select-trigger"
      :class="cn(
        'border-input data-[placeholder]:text-muted-foreground [&_svg:not([class*=\'text-\'])]:text-muted-foreground focus-visible:border-ring focus-visible:ring-ring/50 aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive dark:bg-input/30 dark:hover:bg-input/50 flex w-full items-center justify-between gap-2 rounded-md border bg-transparent px-3 py-2 whitespace-nowrap shadow-xs transition-[color,box-shadow] outline-none focus-visible:ring-[3px] disabled:cursor-not-allowed disabled:opacity-50 *:data-[slot=select-value]:line-clamp-1 *:data-[slot=select-value]:flex *:data-[slot=select-value]:items-center *:data-[slot=select-value]:gap-2 [&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*=\'size-\'])]:size-4',
        triggerSizeClass,
        triggerFixedHeightClass,
        props.class,
      )"
    >
      <SelectValue :placeholder="placeholder" />
      <button
        v-if="showClear"
        type="button"
        tabindex="-1"
        class="ml-auto flex items-center text-muted-foreground hover:text-foreground transition-colors"
        @click="onClear"
      >
        <X class="size-4" />
      </button>
      <SelectIcon v-else as-child>
        <ChevronDown class="size-4 opacity-50 ml-auto" />
      </SelectIcon>
    </SelectTrigger>

    <SelectPortal>
      <SelectContent
        data-slot="select-content"
        position="popper"
        :class="cn(
          'bg-popover text-popover-foreground data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[side=bottom]:slide-in-from-top-2 data-[side=left]:slide-in-from-right-2 data-[side=right]:slide-in-from-left-2 data-[side=top]:slide-in-from-bottom-2 relative z-50 max-h-(--reka-select-content-available-height) min-w-[8rem] overflow-x-hidden overflow-y-auto rounded-md border shadow-md',
          'data-[side=bottom]:translate-y-1 data-[side=left]:-translate-x-1 data-[side=right]:translate-x-1 data-[side=top]:-translate-y-1',
        )"
      >
        <SelectScrollUpButton class="flex cursor-default items-center justify-center py-1">
          <ChevronUp class="size-4" />
        </SelectScrollUpButton>

        <!-- Filter input -->
        <div v-if="filterable" class="sticky top-0 z-10 bg-popover p-1.5 border-b">
          <div class="flex items-center gap-2 px-2 py-1 rounded-sm bg-muted/50">
            <Search class="size-4 shrink-0 text-muted-foreground" />
            <input
              ref="filterInputRef"
              v-model="filterQuery"
              type="text"
              class="flex-1 bg-transparent text-sm outline-none placeholder:text-muted-foreground"
              placeholder="Search..."
              @keydown="onFilterKeydown"
            />
          </div>
        </div>

        <SelectViewport class="p-1 h-[var(--reka-select-trigger-height)] w-full min-w-[var(--reka-select-trigger-width)] scroll-my-1">
          <!-- No results message -->
          <div
            v-if="filterable && !hasFilteredResults"
            class="py-6 text-center text-sm text-muted-foreground"
          >
            No options found.
          </div>

          <!-- Grouped options -->
          <template v-if="isGrouped">
            <SelectGroup
              v-for="(group, gi) in filteredGroupedOptions"
              :key="gi"
            >
              <SelectLabel class="text-muted-foreground px-2 py-1.5 text-xs">
                {{ group.label }}
              </SelectLabel>
              <SelectItem
                v-for="option in group.options"
                :key="optionValue(option)"
                :value="String(optionValue(option))"
                :disabled="option.disabled"
                :class="cn(itemClass)"
              >
                <span class="absolute right-2 flex size-3.5 items-center justify-center">
                  <SelectItemIndicator>
                    <Check class="size-4" />
                  </SelectItemIndicator>
                </span>
                <SelectItemText>{{ optionLabel(option) }}</SelectItemText>
              </SelectItem>
            </SelectGroup>
          </template>

          <!-- Flat options -->
          <template v-else>
            <SelectItem
              v-for="option in filteredFlatOptions"
              :key="optionValue(option)"
              :value="String(optionValue(option))"
              :disabled="option.disabled"
              :class="cn(itemClass)"
            >
              <span class="absolute right-2 flex size-3.5 items-center justify-center">
                <SelectItemIndicator>
                  <Check class="size-4" />
                </SelectItemIndicator>
              </span>
              <SelectItemText>{{ optionLabel(option) }}</SelectItemText>
            </SelectItem>
          </template>
        </SelectViewport>

        <SelectScrollDownButton class="flex cursor-default items-center justify-center py-1">
          <ChevronDown class="size-4" />
        </SelectScrollDownButton>
      </SelectContent>
    </SelectPortal>
  </SelectRoot>
</template>
