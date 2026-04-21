<!--
  EMention @提及输入组件
  在 textarea 中检测 @ 前缀，实时搜索候选项并以弹层展示
  支持 ArrowUp/Down/Enter/Esc 键盘导航，选中后在光标位置插入 @名字
-->
<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { LoaderCircle } from 'lucide-vue-next'
import { cn } from '@/utils/cn'
import type { EMentionProps, EMentionEmits, MentionOption } from './types'

const props = withDefaults(defineProps<EMentionProps>(), {
  modelValue: '',
  options: () => [],
  prefix: '@',
  loading: false,
  disabled: false,
})

const emit = defineEmits<EMentionEmits>()

const textareaRef = ref<HTMLTextAreaElement | null>(null)
const inputValue = ref(props.modelValue ?? '')
const isOpen = ref(false)
const query = ref('')
const activeIndex = ref(0)
// 记录 @ 字符所在位置，选中时用于拼接最终文本
let mentionStart = -1

// 外部 modelValue 同步到内部
watch(() => props.modelValue, (val) => {
  inputValue.value = val ?? ''
})

// 根据 query 过滤候选项（大小写不敏感）
const filteredOptions = computed(() => {
  if (!query.value) return props.options
  return props.options.filter(o =>
    o.label.toLowerCase().includes(query.value.toLowerCase())
  )
})

/**
 * 输入处理：检测光标前最后一个 @ 字符，并判定其后是否构成有效的 mention 片段
 * 片段含空格或换行则视为已结束，关闭候选面板
 */
function handleInput(event: Event) {
  const textarea = event.target as HTMLTextAreaElement
  const val = textarea.value
  inputValue.value = val
  emit('update:modelValue', val)

  const cursor = textarea.selectionStart
  const textBeforeCursor = val.slice(0, cursor)

  const lastPrefixIdx = textBeforeCursor.lastIndexOf(props.prefix ?? '@')

  if (lastPrefixIdx >= 0) {
    const textAfterPrefix = textBeforeCursor.slice(lastPrefixIdx + 1)
    // @ 之后不含空格/换行视为有效提及输入态
    if (!textAfterPrefix.includes(' ') && !textAfterPrefix.includes('\n')) {
      mentionStart = lastPrefixIdx
      query.value = textAfterPrefix
      isOpen.value = true
      activeIndex.value = 0
      return
    }
  }

  isOpen.value = false
}

/**
 * 选中候选项：用 "{prefix}{label} " 替换 @xxx 片段，并把光标落到插入文本之后
 */
function selectOption(option: MentionOption) {
  const val = inputValue.value
  const beforeMention = val.slice(0, mentionStart)
  const afterCursor = val.slice(textareaRef.value?.selectionStart ?? val.length)
  const newVal = `${beforeMention}${props.prefix}${option.label} ${afterCursor}`
  inputValue.value = newVal
  emit('update:modelValue', newVal)
  emit('select', option)
  isOpen.value = false

  // 异步恢复 focus 与光标位置，避免在 blur 之前被覆盖
  setTimeout(() => {
    textareaRef.value?.focus()
    const pos = beforeMention.length + (props.prefix ?? '@').length + option.label.length + 1
    textareaRef.value?.setSelectionRange(pos, pos)
  })
}

/**
 * 键盘导航：上下移动高亮、Enter 选中、Esc 关闭
 */
function handleKeydown(event: KeyboardEvent) {
  if (!isOpen.value) return
  if (event.key === 'ArrowDown') {
    event.preventDefault()
    activeIndex.value = Math.min(activeIndex.value + 1, filteredOptions.value.length - 1)
  } else if (event.key === 'ArrowUp') {
    event.preventDefault()
    activeIndex.value = Math.max(activeIndex.value - 1, 0)
  } else if (event.key === 'Enter' && filteredOptions.value.length > 0) {
    event.preventDefault()
    selectOption(filteredOptions.value[activeIndex.value])
  } else if (event.key === 'Escape') {
    isOpen.value = false
  }
}

/**
 * 失焦延迟关闭面板，留出时间给 mousedown 选中事件先触发
 */
function handleBlur() {
  setTimeout(() => {
    isOpen.value = false
  }, 150)
}
</script>

<template>
  <div :class="cn('relative', props.class)">
    <textarea
      ref="textareaRef"
      :value="inputValue"
      :disabled="props.disabled"
      :placeholder="props.placeholder"
      class="flex min-h-[80px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-xs transition-[color,box-shadow] outline-none placeholder:text-muted-foreground focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px] disabled:cursor-not-allowed disabled:opacity-50 resize-none"
      @input="handleInput"
      @keydown="handleKeydown"
      @blur="handleBlur"
    />

    <div
      v-if="isOpen && (filteredOptions.length > 0 || props.loading)"
      class="absolute z-50 bottom-full mb-1 w-full rounded-md border bg-popover text-popover-foreground shadow-md overflow-hidden"
    >
      <div
        v-if="props.loading"
        class="flex items-center justify-center py-3 text-sm text-muted-foreground gap-2"
      >
        <LoaderCircle class="size-4 animate-spin" />
        Loading...
      </div>
      <ul v-else class="max-h-48 overflow-y-auto p-1">
        <li
          v-for="(option, index) in filteredOptions"
          :key="option.value"
          :class="cn(
            'relative flex cursor-default items-center rounded-sm px-2 py-1.5 text-sm outline-hidden select-none',
            index === activeIndex
              ? 'bg-accent text-accent-foreground'
              : 'hover:bg-accent hover:text-accent-foreground',
          )"
          @mousedown.prevent="selectOption(option)"
        >
          <span class="text-primary font-medium mr-1">{{ props.prefix }}</span>
          {{ option.label }}
        </li>
      </ul>
    </div>
  </div>
</template>
