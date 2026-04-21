<!--
  ETextarea 多行文本输入框
  借助 useSecureValue 避免敏感文本暴露到 HTML attribute，同时处理 IME 输入法与光标保留
  autoResize 开启时根据 minRows/maxRows 自动调整高度；maxRows 溢出改为内部滚动
-->
<script setup lang="ts">
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { cn } from '@/utils/cn'
import { useSecureValue } from '@/composables/useSecureValue'
import type { ETextareaProps, ETextareaEmits } from './types'

const props = withDefaults(defineProps<ETextareaProps>(), {
  disabled: false,
  readonly: false,
  autoResize: false,
  showWordLimit: false,
})

const emit = defineEmits<ETextareaEmits>()

const textareaRef = ref<HTMLTextAreaElement | null>(null)
const lineHeight = ref(0)

const {
  isComposing,
  recordCursor,
  setCursor,
  setNativeValue,
  onCompositionStart,
  onCompositionEnd,
} = useSecureValue(textareaRef, () => props.modelValue)

/** 从 computed style 读取行高（autoResize 计算 minRows/maxRows 时需要），挂载后调用一次 */
function detectLineHeight() {
  if (!textareaRef.value) return
  const computed = window.getComputedStyle(textareaRef.value)
  const lh = parseFloat(computed.lineHeight)
  lineHeight.value = Number.isNaN(lh) ? parseFloat(computed.fontSize) * 1.5 : lh
}

const wordLimitText = computed(() => {
  if (!props.showWordLimit || !props.maxlength) return ''
  const len = props.modelValue?.length ?? 0
  return `${len}/${props.maxlength}`
})

/**
 * 根据当前内容动态调整 textarea 高度
 * 先重置为 auto 以取得真实 scrollHeight，再按 minRows/maxRows 约束
 */
function adjustHeight() {
  if (!props.autoResize || !textareaRef.value) return
  const el = textareaRef.value

  // 先重置为 auto 以取得真实 scrollHeight
  el.style.height = 'auto'
  el.style.minHeight = ''
  el.style.maxHeight = ''
  el.style.overflowY = 'hidden'

  const lh = lineHeight.value || 20

  if (props.minRows) {
    const paddingTop = parseFloat(window.getComputedStyle(el).paddingTop) || 0
    const paddingBottom = parseFloat(window.getComputedStyle(el).paddingBottom) || 0
    const minH = props.minRows * lh + paddingTop + paddingBottom
    el.style.minHeight = `${minH}px`
  }

  if (props.maxRows) {
    const paddingTop = parseFloat(window.getComputedStyle(el).paddingTop) || 0
    const paddingBottom = parseFloat(window.getComputedStyle(el).paddingBottom) || 0
    const maxH = props.maxRows * lh + paddingTop + paddingBottom
    el.style.maxHeight = `${maxH}px`
    if (el.scrollHeight > maxH) {
      el.style.overflowY = 'auto'
    }
  }

  el.style.height = `${el.scrollHeight}px`
}

onMounted(() => {
  detectLineHeight()
  adjustHeight()
})

watch(() => props.modelValue, () => {
  nextTick(() => adjustHeight())
})

async function onInput(event: Event) {
  recordCursor()
  if (isComposing.value) return
  const value = (event.target as HTMLTextAreaElement).value
  emit('update:modelValue', value)
  await nextTick()
  setNativeValue()
  setCursor()
  adjustHeight()
}

function onChange(event: Event) {
  const value = (event.target as HTMLTextAreaElement).value
  emit('change', value)
}

function onBlur(event: FocusEvent) {
  emit('blur', event)
}

function onFocus(event: FocusEvent) {
  emit('focus', event)
}
</script>

<template>
  <div data-slot="textarea-wrapper" class="relative w-full">
    <textarea
      ref="textareaRef"
      data-slot="textarea"
      :placeholder="placeholder"
      :rows="rows"
      :disabled="disabled"
      :readonly="readonly"
      :maxlength="maxlength"
      :class="cn(
        'border-input placeholder:text-muted-foreground focus-visible:border-ring focus-visible:ring-ring/50 aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive dark:bg-input/30 flex min-h-16 w-full rounded-md border bg-transparent px-3 py-2 text-base shadow-xs transition-[color,box-shadow] outline-none focus-visible:ring-[3px] disabled:cursor-not-allowed disabled:opacity-50 md:text-sm',
        autoResize ? 'resize-none overflow-hidden' : '',
        props.class,
      )"
      @input="onInput"
      @change="onChange"
      @blur="onBlur"
      @focus="onFocus"
      @compositionstart="onCompositionStart"
      @compositionend="onCompositionEnd"
    />
    <span
      v-if="showWordLimit && maxlength"
      class="mt-1 block text-right text-xs text-muted-foreground"
    >
      {{ wordLimitText }}
    </span>
  </div>
</template>
