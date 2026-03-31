<script setup lang="ts">
import { Label } from 'reka-ui'
import { cn } from '@/utils/cn'
import type { ELabelProps } from './types'

const props = defineProps<ELabelProps>()
</script>

<template>
  <Label
    data-slot="label"
    :for="props.for"
    :class="cn(
      'flex items-center gap-2 text-sm leading-none font-medium select-none group-data-[disabled=true]:pointer-events-none group-data-[disabled=true]:opacity-50 peer-disabled:cursor-not-allowed peer-disabled:opacity-50',
      props.class,
    )"
  >
    <slot />
  </Label>
</template>
