<script setup lang="ts">
import { cn } from '@/utils/cn'
import type { ELoginLayoutProps } from './types'

const props = defineProps<ELoginLayoutProps>()
</script>

<template>
  <div
    data-slot="login-layout"
    :class="cn('min-h-screen w-full flex items-center justify-center', props.class)"
    :style="background ? { background } : undefined"
  >
    <div
      data-slot="login-layout-card"
      class="w-full max-w-md"
    >
      <!-- Logo / Title area -->
      <div class="mb-8 flex flex-col items-center gap-3 text-center">
        <slot name="logo">
          <img v-if="logo" :src="logo" class="h-10 w-10 object-contain" alt="logo" />
        </slot>
        <h1 v-if="title" class="text-2xl font-bold tracking-tight">{{ title }}</h1>
      </div>

      <!-- Form content -->
      <div class="rounded-lg border bg-card p-8 shadow-sm">
        <slot />
      </div>

      <!-- Footer -->
      <div v-if="$slots.footer" class="mt-6 text-center text-sm text-muted-foreground">
        <slot name="footer" />
      </div>
    </div>
  </div>
</template>
