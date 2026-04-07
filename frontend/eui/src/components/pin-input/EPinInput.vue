<script setup lang="ts">
import { PinInputRoot, PinInputInput } from 'reka-ui'
import { cn } from '@/utils/cn'
import type { EPinInputProps, EPinInputEmits } from './types'

const props = withDefaults(defineProps<EPinInputProps>(), {
  length: 4,
  disabled: false,
  mask: true,
  otp: false,
  type: 'text',
})

const emit = defineEmits<EPinInputEmits>()

function handleUpdate(val: string[]) {
  emit('update:modelValue', val)
  if (val.filter(Boolean).length === props.length) {
    emit('complete', val)
  }
}
</script>

<template>
  <PinInputRoot
    data-slot="pin-input"
    :otp="props.otp"
    :mask="props.mask"
    :type="props.type"
    :model-value="props.modelValue"
    :disabled="props.disabled"
    :class="cn('flex items-center gap-2 has-disabled:opacity-50', props.class)"
    @update:model-value="handleUpdate"
  >
    <div class="flex items-center">
      <PinInputInput
        v-for="(_, idx) in props.length"
        :key="idx"
        :index="idx"
        data-slot="pin-input-slot"
        :class="cn(
          'border-input focus:border-ring focus:ring-ring/50 dark:bg-input/30 relative flex h-9 w-9 items-center justify-center border-y border-r text-sm shadow-xs transition-all outline-none text-center first:rounded-l-md first:border-l last:rounded-r-md focus:z-10 focus:ring-[3px] disabled:cursor-not-allowed',
        )"
      />
    </div>
  </PinInputRoot>
</template>
