<!--
  EInput 输入框组件
  原生 input 的增强封装：前后缀插槽、清空按钮、密码明文切换、字数统计
  使用 useSecureValue 处理中文输入法合成，避免拼音中间态丢字符
-->
<script setup lang="ts">
import { computed, nextTick, ref, shallowRef, useSlots } from 'vue'
import { X, Eye, EyeOff } from 'lucide-vue-next'
import { cn } from '@/utils/cn'
import { useSecureValue } from '@/composables/useSecureValue'
import type { EInputProps, EInputEmits } from './types'

const props = withDefaults(defineProps<EInputProps>(), {
  type: 'text',
  disabled: false,
  readonly: false,
  clearable: false,
  showPassword: false,
  showWordLimit: false,
})

const slots = useSlots()

const emit = defineEmits<EInputEmits>()

const inputRef = shallowRef<HTMLInputElement>()
const passwordVisible = ref(false)

// 处理中文输入法合成事件，避免值在合成期被外部同步打断
const {
  isComposing,
  recordCursor,
  setCursor,
  setNativeValue,
  onCompositionStart,
  onCompositionEnd,
} = useSecureValue(inputRef, () => props.modelValue)

// showPassword 开启时，根据明文/密文切换 type
const inputType = computed(() => {
  if (props.showPassword) {
    return passwordVisible.value ? 'text' : 'password'
  }
  return props.type
})

// 清空按钮显示条件：clearable 开启、有值、非禁用/只读
const showClearButton = computed(() => {
  return props.clearable && props.modelValue && !props.disabled && !props.readonly
})

const hasPrefix = computed(() => !!slots.prefix)
const hasSuffix = computed(() => !!slots.suffix)

// 当前输入长度，用于字数统计
const currentLength = computed(() => {
  if (props.modelValue == null) return 0
  return String(props.modelValue).length
})

const showWordLimitText = computed(() => {
  return props.showWordLimit && props.maxlength != null
})

// 尺寸映射到 Tailwind 类
const sizeClass = computed(() => {
  if (props.size === 'sm') return 'h-8 text-xs'
  if (props.size === 'lg') return 'h-10 text-base'
  return 'h-9 text-base md:text-sm'
})

/**
 * 输入处理：记录光标位置，合成期跳过，合成完成后恢复光标避免跳动
 */
async function onInput(event: Event) {
  recordCursor()
  if (isComposing.value) return
  const value = (event.target as HTMLInputElement).value
  emit('update:modelValue', value)
  await nextTick()
  setNativeValue()
  setCursor()
}

/** change 事件转发 */
function onChange(event: Event) {
  const value = (event.target as HTMLInputElement).value
  emit('change', value)
}

/** blur 事件转发 */
function onBlur(event: FocusEvent) {
  emit('blur', event)
}

/** focus 事件转发 */
function onFocus(event: FocusEvent) {
  emit('focus', event)
}

/** 清空按钮点击：置空值并派发 clear 事件 */
function onClear() {
  emit('update:modelValue', '')
  emit('clear')
}

/** 切换密码明文/密文显示 */
function togglePasswordVisibility() {
  passwordVisible.value = !passwordVisible.value
}
</script>

<template>
  <div
    data-slot="input-root"
    :class="cn('w-full min-w-0', props.class)"
  >
    <div
      data-slot="input-wrapper"
      :class="cn(
        'relative flex min-w-0 w-full items-center',
      )"
    >
      <span
        v-if="hasPrefix"
        data-slot="input-prefix"
        :class="cn('absolute left-2 flex items-center text-muted-foreground')"
      >
        <slot name="prefix" />
      </span>
      <input
        ref="inputRef"
        data-slot="input"
        :type="inputType"
        :placeholder="placeholder"
        :disabled="disabled"
        :readonly="readonly"
        :name="name"
        :maxlength="maxlength"
        :autocomplete="autocomplete"
        :autocorrect="type === 'password' ? 'off' : undefined"
        :spellcheck="type === 'password' ? false : undefined"
        :class="cn(
          'file:text-foreground placeholder:text-muted-foreground selection:bg-primary selection:text-primary-foreground dark:bg-input/30 border-input w-full min-w-0 rounded-md border bg-transparent px-3 py-1 shadow-xs transition-[color,box-shadow] outline-none file:inline-flex file:h-7 file:border-0 file:bg-transparent file:text-sm file:font-medium disabled:pointer-events-none disabled:cursor-not-allowed disabled:opacity-50',
          'focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px]',
          'aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive',
          sizeClass,
          hasPrefix ? 'pl-8' : '',
          (hasSuffix || showClearButton || showPassword) ? 'pr-8' : '',
        )"
        @input="onInput"
        @change="onChange"
        @blur="onBlur"
        @focus="onFocus"
        @compositionstart="onCompositionStart"
        @compositionend="onCompositionEnd"
      />
      <button
        v-if="showClearButton && !showPassword"
        type="button"
        tabindex="-1"
        :class="cn(
          'absolute right-2 flex items-center justify-center text-muted-foreground hover:text-foreground transition-colors',
        )"
        @click="onClear"
      >
        <X class="size-4" />
      </button>
      <button
        v-if="showPassword"
        type="button"
        tabindex="-1"
        :class="cn(
          'absolute right-2 flex items-center justify-center text-muted-foreground hover:text-foreground transition-colors',
        )"
        @click="togglePasswordVisibility"
      >
        <EyeOff v-if="passwordVisible" class="size-4" />
        <Eye v-else class="size-4" />
      </button>
      <span
        v-if="hasSuffix && !showClearButton && !showPassword"
        data-slot="input-suffix"
        :class="cn('absolute right-2 flex items-center text-muted-foreground')"
      >
        <slot name="suffix" />
      </span>
    </div>
    <p
      v-if="showWordLimitText"
      :class="cn('mt-1 text-xs text-muted-foreground text-right')"
    >
      {{ currentLength }}/{{ maxlength }}
    </p>
  </div>
</template>
