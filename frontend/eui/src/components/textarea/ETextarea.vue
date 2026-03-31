<script setup lang="ts">
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { cn } from '@/utils/cn'
import type { ETextareaProps, ETextareaEmits } from './types'

const props = withDefaults(defineProps<ETextareaProps>(), {
  disabled: false,
  readonly: false,
  autoResize: false,
})

const emit = defineEmits<ETextareaEmits>()

const textareaRef = ref<HTMLTextAreaElement | null>(null)

function adjustHeight() {
  if (!props.autoResize || !textareaRef.value) return
  textareaRef.value.style.height = 'auto'
  textareaRef.value.style.height = `${textareaRef.value.scrollHeight}px`
}

onMounted(() => {
  adjustHeight()
})

watch(() => props.modelValue, () => {
  nextTick(() => adjustHeight())
})

function onInput(event: Event) {
  const value = (event.target as HTMLTextAreaElement).value
  emit('update:modelValue', value)
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
  <textarea
    ref="textareaRef"
    data-slot="textarea"
    :value="modelValue"
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
  />
</template>
