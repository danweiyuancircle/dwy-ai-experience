<script setup lang="ts">
import { cn } from '@/utils/cn'
import type { ESkeletonProps } from './types'

const props = defineProps<ESkeletonProps>()
</script>

<template>
  <div
    data-slot="skeleton"
    :class="cn('animate-pulse rounded-md bg-primary/10', props.class)"
  />
</template>
