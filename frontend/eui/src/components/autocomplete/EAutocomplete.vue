<!--
  EAutocomplete 自动补全输入组件
  输入时通过外部 fetchSuggestions 异步获取候选项，以下拉面板展示
  支持键盘导航（上下方向键 / Enter / Esc）与输入法合成安全处理
-->
<script setup lang="ts">
import { ref, shallowRef, watch, computed, nextTick } from 'vue'
import { LoaderCircle } from 'lucide-vue-next'
import { cn } from '@/utils/cn'
import { useSecureValue } from '@/composables/useSecureValue'
import type { EAutocompleteProps, EAutocompleteEmits, AutocompleteOption } from './types'

const props = withDefaults(defineProps<EAutocompleteProps>(), {
  modelValue: '',
  debounce: 300,
  disabled: false,
})

const emit = defineEmits<EAutocompleteEmits>()

const inputRef = shallowRef<HTMLInputElement>()
const inputValue = ref(props.modelValue ?? '')
const suggestions = ref<AutocompleteOption[]>([])
const isOpen = ref(false)
const isLoading = ref(false)
const activeIndex = ref(-1)
let debounceTimer: ReturnType<typeof setTimeout> | null = null

// 使用 useSecureValue 处理中文输入法合成，避免拼音中间态触发补全
const {
  isComposing,
  recordCursor,
  setCursor,
  setNativeValue,
  onCompositionStart,
  onCompositionEnd,
} = useSecureValue(inputRef, () => inputValue.value)

// 外部 modelValue 变化时同步到内部输入值
watch(() => props.modelValue, (val) => {
  inputValue.value = val ?? ''
})

/**
 * 输入处理：记录光标、同步值、防抖触发 fetchSuggestions
 * 合成态（输入法中间态）下跳过，避免每个拼音字母都发起请求
 */
async function handleInput(event: Event) {
  recordCursor()
  if (isComposing.value) return
  const value = (event.target as HTMLInputElement).value
  inputValue.value = value
  emit('update:modelValue', value)
  emit('change', value)
  activeIndex.value = -1
  await nextTick()
  setNativeValue()
  setCursor()

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

/**
 * 选中某个下拉项：回填 label 到输入框并关闭面板
 */
function selectOption(option: AutocompleteOption) {
  inputValue.value = option.label
  emit('update:modelValue', option.label)
  emit('select', option)
  isOpen.value = false
  nextTick(setNativeValue)
}

/**
 * 键盘导航：上下键移动高亮、Enter 选中、Esc 关闭
 */
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

/**
 * 失焦延迟关闭面板，留出空间让 mousedown 选中事件先触发
 */
function handleBlur() {
  setTimeout(() => {
    isOpen.value = false
  }, 150)
}
</script>

<template>
  <div :class="cn('relative', props.class)">
    <input
      ref="inputRef"
      :disabled="props.disabled"
      :placeholder="props.placeholder"
      type="text"
      :class="cn(
        'flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-xs transition-[color,box-shadow] outline-none placeholder:text-muted-foreground focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px] disabled:cursor-not-allowed disabled:opacity-50',
      )"
      @input="handleInput"
      @keydown="handleKeydown"
      @blur="handleBlur"
      @compositionstart="onCompositionStart"
      @compositionend="onCompositionEnd"
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
