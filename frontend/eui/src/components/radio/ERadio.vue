<!--
  ERadio 单选框组件
  基于 reka-ui RadioGroup 封装，通过 options 渲染一组选项
  optionType=default 呈现圆点样式，optionType=button 呈现相连的按钮组样式
  与 reka 通信时 value 用 string（原语限制）；对外 emit 经 options 还原原始 number/string 类型，对齐 ESelect
-->
<script setup lang="ts">
import { computed } from 'vue'
import { RadioGroupRoot, RadioGroupItem, RadioGroupIndicator } from 'reka-ui'
import { cn } from '@/utils/cn'
import type { ERadioProps, ERadioEmits } from './types'

const props = withDefaults(defineProps<ERadioProps>(), {
  options: () => [],
  disabled: false,
  direction: 'horizontal',
  optionType: 'default',
  border: false,
  size: 'default',
})

const emit = defineEmits<ERadioEmits>()

/**
 * reka-ui RadioGroup 只认 string value；对外按 options 还原原始类型，
 * 避免 number option 被强制成 string 破坏 v-model 类型契约。
 */
function onUpdate(value: string | number | bigint | Record<string, any> | null) {
  if (value == null) {
    emit('update:modelValue', '')
    emit('change', '')
    return
  }
  const strValue = String(value)
  const found = props.options.find((o) => String(o.value) === strValue)
  const finalValue = found ? found.value : strValue
  emit('update:modelValue', finalValue)
  emit('change', finalValue)
}

/** 默认圆点模式下的尺寸 class（控制圆点大小、文字、内边距） */
const sizeClasses = computed(() => {
  const map: Record<string, { radio: string; text: string; padding: string }> = {
    sm: { radio: 'size-3.5', text: 'text-xs', padding: 'px-2 py-1.5' },
    default: { radio: 'size-4', text: 'text-sm', padding: 'px-3 py-2' },
    lg: { radio: 'size-5', text: 'text-base', padding: 'px-4 py-2.5' },
  }
  return map[props.size]
})

/** 按钮组模式下的尺寸 class */
const buttonSizeClasses = computed(() => {
  const map: Record<string, string> = {
    sm: 'px-3 py-1 text-xs',
    default: 'px-4 py-2 text-sm',
    lg: 'px-5 py-2.5 text-base',
  }
  return map[props.size]
})
</script>

<template>
  <RadioGroupRoot
    data-slot="radio-group"
    :model-value="modelValue !== undefined ? String(modelValue) : undefined"
    :disabled="disabled"
    :class="cn(
      optionType === 'button'
        ? 'inline-flex'
        : direction === 'horizontal' ? 'flex flex-row gap-4 flex-wrap' : 'grid gap-3',
      props.class,
    )"
    @update:model-value="onUpdate"
  >
    <!-- Button mode -->
    <template v-if="optionType === 'button'">
      <RadioGroupItem
        v-for="(option, index) in options"
        :key="option.value"
        :value="String(option.value)"
        :disabled="disabled || option.disabled"
        data-slot="radio-button-item"
        :class="cn(
          'inline-flex items-center justify-center font-medium transition-colors outline-none select-none',
          'border focus-visible:ring-ring/50 focus-visible:ring-[3px]',
          buttonSizeClasses,
          // Joined borders: first gets left rounded, last gets right rounded, middle gets no rounding
          index === 0 && 'rounded-l-md',
          index === options.length - 1 && 'rounded-r-md',
          index > 0 && '-ml-px',
          // Checked vs unchecked
          String(modelValue) === String(option.value)
            ? 'bg-primary text-primary-foreground border-primary z-10'
            : 'bg-background text-foreground border-input hover:bg-accent hover:text-accent-foreground',
          (disabled || option.disabled) ? 'cursor-not-allowed opacity-50' : 'cursor-pointer',
        )"
      >
        {{ option.label }}
      </RadioGroupItem>
    </template>

    <!-- Default radio dot mode -->
    <template v-else>
      <label
        v-for="option in options"
        :key="option.value"
        :class="cn(
          'flex items-center gap-2',
          (disabled || option.disabled) ? 'cursor-not-allowed opacity-50' : 'cursor-pointer',
          border && 'border rounded-md transition-colors',
          border && sizeClasses.padding,
          border && String(modelValue) === String(option.value) && 'border-primary',
        )"
      >
        <RadioGroupItem
          data-slot="radio-group-item"
          :value="String(option.value)"
          :disabled="disabled || option.disabled"
          :class="cn(
            'border-input text-primary focus-visible:border-ring focus-visible:ring-ring/50 aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive dark:bg-input/30 aspect-square shrink-0 rounded-full border shadow-xs transition-[color,box-shadow] outline-none focus-visible:ring-[3px] disabled:cursor-not-allowed disabled:opacity-50',
            sizeClasses.radio,
          )"
        >
          <RadioGroupIndicator
            data-slot="radio-group-indicator"
            class="relative flex items-center justify-center"
          >
            <span :class="cn(
              'fill-primary absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 rounded-full bg-primary',
              size === 'sm' ? 'size-1.5' : size === 'lg' ? 'size-2.5' : 'size-2',
            )" />
          </RadioGroupIndicator>
        </RadioGroupItem>
        <span :class="cn('leading-none select-none', sizeClasses.text)">{{ option.label }}</span>
      </label>
    </template>
  </RadioGroupRoot>
</template>
