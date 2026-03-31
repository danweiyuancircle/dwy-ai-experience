<script setup lang="ts">
import { computed } from 'vue'
import { Check, ChevronDown, ChevronUp, X } from 'lucide-vue-next'
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
})

const emit = defineEmits<ESelectEmits>()

/** Check if options are grouped (contain an options array inside) */
const isGrouped = computed(() => {
  return (
    Array.isArray(props.options) &&
    props.options.length > 0 &&
    'options' in (props.options[0] as any)
  )
})

const flatOptions = computed(() => {
  if (!props.options || props.options.length === 0) return []
  if (isGrouped.value) {
    return (props.options as GroupedOption[]).flatMap((g) => g.options)
  }
  return props.options as Option[]
})

function optionValue(option: Record<string, any>): string | number {
  return option[props.valueKey] as string | number
}

function optionLabel(option: Record<string, any>): string {
  return option[props.labelKey] as string
}

const groupedOptions = computed((): GroupedOption[] => {
  if (!isGrouped.value) return []
  return props.options as GroupedOption[]
})

const triggerSizeClass = computed(() => {
  if (props.size === 'sm') return 'h-8 text-xs'
  if (props.size === 'lg') return 'h-10 text-base'
  return 'h-9 text-sm'
})

const modelStr = computed(() => {
  if (props.modelValue === undefined) return undefined
  return String(props.modelValue)
})

function onUpdate(value: string) {
  // Find original typed value from options
  const found = flatOptions.value.find((o) => String(optionValue(o)) === value)
  const finalValue = found ? optionValue(found) : value
  emit('update:modelValue', finalValue)
  emit('change', finalValue)
}

function onOpenChange(open: boolean) {
  emit('visible-change', open)
}

function onClear(event: MouseEvent) {
  event.stopPropagation()
  emit('update:modelValue', undefined)
  emit('change', undefined)
}
</script>

<template>
  <SelectRoot
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
        props.class,
      )"
    >
      <SelectValue :placeholder="placeholder" />
      <button
        v-if="clearable && modelValue !== undefined && modelValue !== ''"
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

        <SelectViewport class="p-1 h-[var(--reka-select-trigger-height)] w-full min-w-[var(--reka-select-trigger-width)] scroll-my-1">
          <!-- Grouped options -->
          <template v-if="isGrouped">
            <SelectGroup
              v-for="(group, gi) in groupedOptions"
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
                :class="cn(
                  'focus:bg-accent focus:text-accent-foreground [&_svg:not([class*=\'text-\'])]:text-muted-foreground relative flex w-full cursor-default items-center gap-2 rounded-sm py-1.5 pr-8 pl-2 text-sm outline-hidden select-none data-[disabled]:pointer-events-none data-[disabled]:opacity-50 [&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*=\'size-\'])]:size-4',
                )"
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
              v-for="option in flatOptions"
              :key="optionValue(option)"
              :value="String(optionValue(option))"
              :disabled="option.disabled"
              :class="cn(
                'focus:bg-accent focus:text-accent-foreground [&_svg:not([class*=\'text-\'])]:text-muted-foreground relative flex w-full cursor-default items-center gap-2 rounded-sm py-1.5 pr-8 pl-2 text-sm outline-hidden select-none data-[disabled]:pointer-events-none data-[disabled]:opacity-50 [&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*=\'size-\'])]:size-4',
              )"
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
