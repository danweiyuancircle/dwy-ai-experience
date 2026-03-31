<script setup lang="ts">
import { computed, ref } from 'vue'
import { Check, ChevronsUpDown, Search } from 'lucide-vue-next'
import {
  ComboboxRoot,
  ComboboxAnchor,
  ComboboxTrigger,
  ComboboxInput,
  ComboboxPortal,
  ComboboxContent,
  ComboboxViewport,
  ComboboxEmpty,
  ComboboxItem,
  ComboboxItemIndicator,
} from 'reka-ui'
import { cn } from '@/utils/cn'
import type { Option } from '@/types'
import type { EComboboxProps, EComboboxEmits } from './types'

const props = withDefaults(defineProps<EComboboxProps>(), {
  options: () => [],
  placeholder: 'Select an option...',
  disabled: false,
  emptyText: 'No options found.',
})

const emit = defineEmits<EComboboxEmits>()

const searchValue = ref('')

const modelStr = computed(() => {
  return props.modelValue !== undefined ? String(props.modelValue) : undefined
})

const selectedLabel = computed(() => {
  const found = props.options.find((o) => String(o.value) === modelStr.value)
  return found ? found.label : undefined
})

function onUpdate(val: string | undefined) {
  const found = props.options.find((o) => String(o.value) === val)
  const finalValue = found ? found.value : val
  emit('update:modelValue', finalValue as string | number | undefined)
  emit('change', finalValue as string | number | undefined)
}
</script>

<template>
  <ComboboxRoot
    :model-value="modelStr"
    :disabled="disabled"
    :filter-function="(list: Option[], term: string) => list.filter(o => o.label.toLowerCase().includes(term.toLowerCase()))"
    @update:model-value="onUpdate"
  >
    <ComboboxAnchor
      :class="cn(
        'flex h-9 w-full items-center justify-between rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-xs ring-offset-background',
        'placeholder:text-muted-foreground',
        'focus-within:outline-none focus-within:ring-2 focus-within:ring-ring focus-within:ring-offset-2',
        'disabled:cursor-not-allowed disabled:opacity-50',
        props.class,
      )"
    >
      <ComboboxInput
        :display-value="() => selectedLabel ?? ''"
        :placeholder="placeholder"
        class="flex-1 bg-transparent outline-none placeholder:text-muted-foreground"
      />
      <ComboboxTrigger class="ml-2 shrink-0 opacity-50">
        <ChevronsUpDown class="size-4" />
      </ComboboxTrigger>
    </ComboboxAnchor>

    <ComboboxPortal>
      <ComboboxContent
        position="popper"
        :side-offset="4"
        :class="cn(
          'z-50 w-[var(--reka-combobox-trigger-width)] min-w-[8rem] overflow-hidden rounded-md border bg-popover text-popover-foreground shadow-md',
          'data-[state=open]:animate-in data-[state=closed]:animate-out',
          'data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0',
          'data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95',
          'data-[side=bottom]:slide-in-from-top-2 data-[side=top]:slide-in-from-bottom-2',
        )"
      >
        <ComboboxViewport class="max-h-[300px] scroll-py-1 overflow-x-hidden overflow-y-auto p-1">
          <ComboboxEmpty class="py-6 text-center text-sm text-muted-foreground">
            {{ emptyText }}
          </ComboboxEmpty>
          <ComboboxItem
            v-for="option in options"
            :key="String(option.value)"
            :value="String(option.value)"
            :disabled="option.disabled"
            :class="cn(
              'relative flex cursor-default select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none',
              'data-[highlighted]:bg-accent data-[highlighted]:text-accent-foreground',
              'data-[disabled]:pointer-events-none data-[disabled]:opacity-50',
            )"
          >
            <ComboboxItemIndicator class="mr-2">
              <Check class="size-4" />
            </ComboboxItemIndicator>
            {{ option.label }}
          </ComboboxItem>
        </ComboboxViewport>
      </ComboboxContent>
    </ComboboxPortal>
  </ComboboxRoot>
</template>
