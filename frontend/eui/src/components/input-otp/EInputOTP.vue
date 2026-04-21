<!--
  EInputOTP 一次性验证码输入组件
  基于 reka-ui PinInput 原语，默认 6 位数字
  填满所有格子时派发 complete 事件，便于自动提交
-->
<script setup lang="ts">
import { computed } from 'vue'
import { PinInputRoot, PinInputInput } from 'reka-ui'
import { cn } from '@/utils/cn'
import type { EInputOTPProps, EInputOTPEmits } from './types'

const props = withDefaults(defineProps<EInputOTPProps>(), {
  length: 6,
  disabled: false,
})

const emit = defineEmits<EInputOTPEmits>()

// 将字符串 modelValue 转为字符数组供 reka-ui PinInput 使用
const pinValue = computed(() => {
  if (!props.modelValue) return []
  return props.modelValue.split('')
})

/**
 * 处理输入更新：拼回字符串后派发，填满位数时额外触发 complete
 */
function handleUpdate(val: string[]) {
  const str = val.join('')
  emit('update:modelValue', str)
  if (str.length === props.length) {
    emit('complete', str)
  }
}
</script>

<template>
  <PinInputRoot
    data-slot="input-otp"
    :otp="true"
    :model-value="pinValue"
    :disabled="props.disabled"
    :class="cn('flex items-center gap-2 has-disabled:opacity-50', props.class)"
    @update:model-value="handleUpdate"
  >
    <div data-slot="input-otp-group" class="flex items-center">
      <PinInputInput
        v-for="(_, idx) in props.length"
        :key="idx"
        :index="idx"
        :placeholder="props.placeholder"
        data-slot="input-otp-slot"
        :class="cn(
          'border-input focus:border-ring focus:ring-ring/50 dark:bg-input/30 relative flex h-9 w-9 items-center justify-center border-y border-r text-sm shadow-xs transition-all outline-none text-center first:rounded-l-md first:border-l last:rounded-r-md focus:z-10 focus:ring-[3px] disabled:cursor-not-allowed',
        )"
      />
    </div>
  </PinInputRoot>
</template>
