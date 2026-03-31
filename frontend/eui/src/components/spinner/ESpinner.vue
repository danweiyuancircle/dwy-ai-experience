<script setup lang="ts">
import { LoaderCircle } from 'lucide-vue-next'
import { cn } from '@/utils/cn'
import type { ESpinnerProps } from './types'

const props = withDefaults(defineProps<ESpinnerProps>(), {
  size: 'default',
})

const sizeClasses = {
  sm: 'size-3',
  default: 'size-4',
  lg: 'size-6',
}
</script>

<template>
  <LoaderCircle
    role="status"
    aria-label="Loading"
    :class="cn('animate-spin', sizeClasses[props.size], props.class)"
  />
</template>
