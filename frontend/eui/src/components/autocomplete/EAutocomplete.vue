<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { LoaderCircle } from 'lucide-vue-next'
import { cn } from '@/utils/cn'
import type { EAutocompleteProps, EAutocompleteEmits, AutocompleteOption } from './types'

const props = withDefaults(defineProps<EAutocompleteProps>(), {
  modelValue: '',
  debounce: 300,
  disabled: false,
})

const emit = defineEmits<EAutocompleteEmits>()

const inputValue = ref(props.modelValue ?? '')
const suggestions = ref<AutocompleteOption[]>([])
const isOpen = ref(false)
const isLoading = ref(false)
const activeIndex = ref(-1)
let debounceTimer: ReturnType<typeof setTimeout> | null = null

watch(() => props.modelValue, (val) => {
  inputValue.value = val ?? ''
})

async function handleInput(event: Event) {
  const value = (event.target as HTMLInputElement).value
  inputValue.value = value
  emit('update:modelValue', value)
  emit('change', value)
  activeIndex.value = -1

  if (!props.fetchSuggestions) return

  if (debounceTimer) clearTimeout(debounceTimer)
  debounceTimer = setTimeout(async () => {
    if (!value.trim()) {
      suggestions.value = []
      isOpen.value = false
      return
    }
    try {
      isLoading.value = true
      suggestions.value = await props.fetchSuggestions!(value)
      isOpen.value = suggestions.value.length > 0
    } finally {
      isLoading.value = false
    }
  }, props.debounce)
}

function selectOption(option: AutocompleteOption) {
  inputValue.value = option.label
  emit('update:modelValue', option.label)
  emit('select', option)
  isOpen.value = false
}

function handleKeydown(event: KeyboardEvent) {
  if (!isOpen.value) return
  if (event.key === 'ArrowDown') {
    event.preventDefault()
    activeIndex.value = Math.min(activeIndex.value + 1, suggestions.value.length - 1)
  } else if (event.key === 'ArrowUp') {
    event.preventDefault()
    activeIndex.value = Math.max(activeIndex.value - 1, -1)
  } else if (event.key === 'Enter' && activeIndex.value >= 0) {
    event.preventDefault()
    selectOption(suggestions.value[activeIndex.value])
  } else if (event.key === 'Escape') {
    isOpen.value = false
  }
}

function handleBlur() {
  setTimeout(() => {
    isOpen.value = false
  }, 150)
}
</script>

<template>
  <div :class="cn('relative', props.class)">
    <input
      :value="inputValue"
      :disabled="props.disabled"
      :placeholder="props.placeholder"
      type="text"
      :class="cn(
        'flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-xs transition-[color,box-shadow] outline-none placeholder:text-muted-foreground focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px] disabled:cursor-not-allowed disabled:opacity-50',
      )"
      @input="handleInput"
      @keydown="handleKeydown"
      @blur="handleBlur"
    />
    <LoaderCircle
      v-if="isLoading"
      class="absolute right-3 top-1/2 -translate-y-1/2 size-4 animate-spin text-muted-foreground"
    />
    <div
      v-if="isOpen && suggestions.length > 0"
      class="absolute z-50 top-full mt-1 w-full rounded-md border bg-popover text-popover-foreground shadow-md overflow-hidden"
    >
      <ul class="max-h-60 overflow-y-auto p-1">
        <li
          v-for="(option, index) in suggestions"
          :key="option.value"
          :class="cn(
            'relative flex cursor-default items-center rounded-sm px-2 py-1.5 text-sm outline-hidden select-none',
            index === activeIndex
              ? 'bg-accent text-accent-foreground'
              : 'hover:bg-accent hover:text-accent-foreground',
          )"
          @mousedown.prevent="selectOption(option)"
        >
          {{ option.label }}
        </li>
      </ul>
    </div>
  </div>
</template>
