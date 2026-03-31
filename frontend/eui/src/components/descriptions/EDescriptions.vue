<script setup lang="ts">
import { cn } from '@/utils/cn'
import type { EDescriptionsProps } from './types'

const props = withDefaults(defineProps<EDescriptionsProps>(), {
  items: () => [],
  columns: 2,
  bordered: false,
})
</script>

<template>
  <div :class="cn('text-sm', props.class)">
    <div v-if="props.title || $slots.title" class="mb-3 font-semibold text-base">
      <slot name="title">{{ props.title }}</slot>
    </div>
    <div
      :class="cn(
        'grid gap-px',
        props.bordered ? 'rounded-md border overflow-hidden bg-border' : 'gap-y-3',
      )"
      :style="{ gridTemplateColumns: `repeat(${props.columns * 2}, minmax(0, 1fr))` }"
    >
      <template v-for="(item, index) in props.items" :key="index">
        <!-- Label -->
        <div
          :class="cn(
            'text-muted-foreground font-medium',
            props.bordered
              ? 'bg-muted/50 px-4 py-3'
              : 'py-1',
          )"
          :style="{ gridColumn: `span ${item.span ?? 1}` }"
        >
          <slot :name="`label-${index}`">{{ item.label }}</slot>
        </div>
        <!-- Value -->
        <div
          :class="cn(
            props.bordered
              ? 'bg-background px-4 py-3'
              : 'py-1',
          )"
          :style="{ gridColumn: `span ${item.span ?? 1}` }"
        >
          <slot :name="`value-${index}`">{{ item.value }}</slot>
        </div>
      </template>
    </div>
  </div>
</template>
