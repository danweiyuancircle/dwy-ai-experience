<script setup lang="ts">
import { cn } from '@/utils/cn'
import type { EEmptyProps } from './types'

const props = defineProps<EEmptyProps>()
</script>

<template>
  <div
    data-slot="empty"
    :class="cn(
      'flex min-w-0 flex-1 flex-col items-center justify-center gap-6 text-balance rounded-lg border-dashed p-6 text-center md:p-12',
      props.class,
    )"
  >
    <div
      v-if="$slots.icon || icon"
      data-slot="empty-icon"
      class="mb-2 flex shrink-0 items-center justify-center bg-muted text-foreground size-10 rounded-lg [&_svg:not([class*='size-'])]:size-6"
    >
      <slot name="icon">{{ icon }}</slot>
    </div>
    <div
      data-slot="empty-content"
      class="flex w-full min-w-0 max-w-sm flex-col items-center gap-4 text-balance text-sm"
    >
      <div
        data-slot="empty-header"
        class="flex max-w-sm flex-col items-center gap-2 text-center"
      >
        <div
          v-if="title || $slots.title"
          data-slot="empty-title"
          class="text-lg font-medium tracking-tight"
        >
          <slot name="title">{{ title }}</slot>
        </div>
        <p
          v-if="description || $slots.description"
          data-slot="empty-description"
          class="text-muted-foreground text-sm/relaxed"
        >
          <slot name="description">{{ description }}</slot>
        </p>
      </div>
      <slot />
    </div>
  </div>
</template>
