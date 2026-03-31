<script setup lang="ts">
import { AvatarRoot, AvatarImage, AvatarFallback } from 'reka-ui'
import { cn } from '@/utils/cn'
import type { EAvatarProps } from './types'

const props = withDefaults(defineProps<EAvatarProps>(), {
  size: 'default',
})

const sizeClasses = {
  sm: 'size-8',
  default: 'size-10',
  lg: 'size-12',
}
</script>

<template>
  <AvatarRoot
    data-slot="avatar"
    :class="cn('relative flex shrink-0 overflow-hidden rounded-full', sizeClasses[props.size], props.class)"
  >
    <AvatarImage
      v-if="src"
      data-slot="avatar-image"
      :src="src"
      :alt="alt"
      class="aspect-square size-full"
    />
    <AvatarFallback
      data-slot="avatar-fallback"
      class="bg-muted flex size-full items-center justify-center rounded-full"
    >
      <slot>{{ fallback }}</slot>
    </AvatarFallback>
  </AvatarRoot>
</template>
