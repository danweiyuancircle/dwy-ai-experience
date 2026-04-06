<script setup lang="ts">
import { computed } from 'vue'
import { SwitchRoot, SwitchThumb } from 'reka-ui'
import { cn } from '@/utils/cn'
import type { ESwitchProps, ESwitchEmits } from './types'

const props = withDefaults(defineProps<ESwitchProps>(), {
  disabled: false,
})

const emit = defineEmits<ESwitchEmits>()

const checked = computed({
  get: () => props.modelValue ?? false,
  set: (val: boolean) => {
    emit('update:modelValue', val)
    emit('change', val)
  },
})

const sizeClass = computed(() => {
  if (props.size === 'sm') return 'h-[0.9rem] w-6'
  if (props.size === 'lg') return 'h-[1.4rem] w-10'
  return 'h-[1.15rem] w-8'
})

const thumbSizeClass = computed(() => {
  if (props.size === 'sm') return 'size-3'
  if (props.size === 'lg') return 'size-5'
  return 'size-4'
})
</script>

<template>
  <div
    data-slot="switch-wrapper"
    :class="cn(
      'flex items-center gap-2',
      disabled ? 'cursor-not-allowed opacity-50' : 'cursor-pointer',
    )"
  >
    <SwitchRoot
      v-model="checked"
      data-slot="switch"
      :disabled="disabled"
      :class="cn(
        'peer data-[state=checked]:bg-primary data-[state=unchecked]:bg-input focus-visible:border-ring focus-visible:ring-ring/50 dark:data-[state=unchecked]:bg-input/80 inline-flex shrink-0 items-center rounded-full border border-transparent shadow-xs transition-all outline-none focus-visible:ring-[3px] disabled:cursor-not-allowed disabled:opacity-50',
        sizeClass,
        props.class,
      )"
    >
      <SwitchThumb
        data-slot="switch-thumb"
        :class="cn(
          'bg-background dark:data-[state=unchecked]:bg-foreground dark:data-[state=checked]:bg-primary-foreground pointer-events-none block rounded-full ring-0 transition-transform data-[state=checked]:translate-x-[calc(100%-2px)] data-[state=unchecked]:translate-x-0',
          thumbSizeClass,
        )"
      />
    </SwitchRoot>
    <slot>
      <span v-if="label" class="text-sm leading-none select-none">{{ label }}</span>
    </slot>
  </div>
</template>
