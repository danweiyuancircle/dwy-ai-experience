<!--
  ENumberField 数字输入框组件
  基于 reka-ui NumberField 封装，内置加减按钮，支持步长、精度、最小/最大值约束
  controlsPosition=right 按钮叠于右侧，default 左右分布
-->
<script setup lang="ts">
import { computed } from 'vue'
import { Minus, Plus } from 'lucide-vue-next'
import {
  NumberFieldDecrement,
  NumberFieldIncrement,
  NumberFieldInput,
  NumberFieldRoot,
} from 'reka-ui'
import { cn } from '@/utils/cn'
import type { ENumberFieldProps, ENumberFieldEmits } from './types'

const props = withDefaults(defineProps<ENumberFieldProps>(), {
  disabled: false,
  controlsPosition: 'default',
  readonly: false,
})

const emit = defineEmits<ENumberFieldEmits>()

const sizeClass = {
  sm: 'h-8 text-xs',
  md: 'h-9 text-sm',
  lg: 'h-10 text-base',
}

const formatOptions = computed(() => {
  if (props.precision === undefined) return undefined
  return {
    minimumFractionDigits: props.precision,
    maximumFractionDigits: props.precision,
  }
})

/**
 * 数值变更回调：同时抛出 v-model 更新与 change 事件
 * change 与 update:modelValue 同步触发，便于表单校验场景监听
 */
function onUpdate(value: number) {
  emit('update:modelValue', value)
  emit('change', value)
}
</script>

<template>
  <NumberFieldRoot
    data-slot="number-field"
    :model-value="modelValue"
    :min="min"
    :max="max"
    :step="step"
    :disabled="disabled"
    :readonly="readonly"
    :format-options="formatOptions"
    :class="cn('grid gap-1.5', props.class)"
    @update:model-value="onUpdate"
  >
    <!-- Controls position: right -->
    <div
      v-if="controlsPosition === 'right'"
      class="relative"
    >
      <NumberFieldInput
        data-slot="input"
        :placeholder="placeholder"
        :class="cn(
          'flex w-full rounded-md border border-input bg-transparent py-1 pr-9 pl-3 text-left shadow-xs transition-[color,box-shadow] placeholder:text-muted-foreground outline-none focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px] disabled:cursor-not-allowed disabled:opacity-50',
          size ? sizeClass[size] : sizeClass.md,
        )"
      />

      <div class="absolute right-0 top-0 flex h-full flex-col border-l border-input">
        <NumberFieldIncrement
          data-slot="increment"
          :class="cn(
            'flex flex-1 items-center justify-center px-1.5 hover:bg-accent rounded-tr-md disabled:cursor-not-allowed disabled:opacity-20',
          )"
        >
          <Plus class="h-3 w-3" />
        </NumberFieldIncrement>

        <div class="border-t border-input" />

        <NumberFieldDecrement
          data-slot="decrement"
          :class="cn(
            'flex flex-1 items-center justify-center px-1.5 hover:bg-accent rounded-br-md disabled:cursor-not-allowed disabled:opacity-20',
          )"
        >
          <Minus class="h-3 w-3" />
        </NumberFieldDecrement>
      </div>
    </div>

    <!-- Controls position: default (left and right) -->
    <div
      v-else
      class="relative [&>[data-slot=input]]:has-[[data-slot=increment]]:pr-10 [&>[data-slot=input]]:has-[[data-slot=decrement]]:pl-10"
    >
      <NumberFieldDecrement
        data-slot="decrement"
        :class="cn(
          'absolute top-1/2 -translate-y-1/2 left-0 p-3 disabled:cursor-not-allowed disabled:opacity-20',
        )"
      >
        <Minus class="h-4 w-4" />
      </NumberFieldDecrement>

      <NumberFieldInput
        data-slot="input"
        :placeholder="placeholder"
        :class="cn(
          'flex w-full rounded-md border border-input bg-transparent py-1 text-center shadow-xs transition-[color,box-shadow] placeholder:text-muted-foreground outline-none focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px] disabled:cursor-not-allowed disabled:opacity-50',
          size ? sizeClass[size] : sizeClass.md,
        )"
      />

      <NumberFieldIncrement
        data-slot="increment"
        :class="cn(
          'absolute top-1/2 -translate-y-1/2 right-0 p-3 disabled:cursor-not-allowed disabled:opacity-20',
        )"
      >
        <Plus class="h-4 w-4" />
      </NumberFieldIncrement>
    </div>
  </NumberFieldRoot>
</template>
