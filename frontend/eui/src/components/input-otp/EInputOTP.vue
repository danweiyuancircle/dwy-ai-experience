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

// Convert string modelValue to array for reka-ui PinInput
const pinValue = computed(() => {
  if (!props.modelValue) return []
  return props.modelValue.split('')
})

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
