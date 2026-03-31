<script setup lang="ts">
import { computed } from 'vue'
import { cn } from '@/utils/cn'
import type { EStatisticProps } from './types'

const props = defineProps<EStatisticProps>()

const formattedValue = computed(() => {
  if (props.value === undefined || props.value === null) return '-'
  if (typeof props.value === 'string') return props.value
  if (props.precision !== undefined) {
    return props.value.toFixed(props.precision)
  }
  return props.value.toLocaleString()
})
</script>

<template>
  <div :class="cn('flex flex-col gap-1', props.class)">
    <div class="text-sm text-muted-foreground">
      <slot name="title">{{ props.title }}</slot>
    </div>
    <div class="flex items-baseline gap-1">
      <span v-if="props.prefix || $slots.prefix" class="text-base text-muted-foreground">
        <slot name="prefix">{{ props.prefix }}</slot>
      </span>
      <span class="text-3xl font-semibold tracking-tight">
        <slot>{{ formattedValue }}</slot>
      </span>
      <span v-if="props.suffix || $slots.suffix" class="text-base text-muted-foreground">
        <slot name="suffix">{{ props.suffix }}</slot>
      </span>
    </div>
  </div>
</template>
