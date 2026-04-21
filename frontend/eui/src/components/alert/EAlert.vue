<!--
  EAlert 警告提示组件
  用于页面级静态提示，区别于 toast 的瞬时反馈
  支持 icon / title / description / 关闭按钮，可通过 variant 切换危险态
-->
<script setup lang="ts">
import { X } from 'lucide-vue-next'
import { cn } from '@/utils/cn'
import { alertVariants } from './types'
import type { EAlertProps, EAlertEmits } from './types'

const props = withDefaults(defineProps<EAlertProps>(), {
  closable: false,
})

const emit = defineEmits<EAlertEmits>()
</script>

<template>
  <div
    data-slot="alert"
    :class="cn(alertVariants({ variant }), props.class)"
    role="alert"
  >
    <!-- icon slot -->
    <slot name="icon" />

    <!-- title -->
    <div
      v-if="title || $slots.title"
      data-slot="alert-title"
      class="col-start-2 line-clamp-1 min-h-4 font-medium tracking-tight"
    >
      <slot name="title">{{ title }}</slot>
    </div>

    <!-- description / default slot -->
    <div
      v-if="description || $slots.default"
      data-slot="alert-description"
      class="text-muted-foreground col-start-2 grid justify-items-start gap-1 text-sm [&_p]:leading-relaxed"
    >
      <slot>{{ description }}</slot>
    </div>

    <!-- close button -->
    <button
      v-if="closable"
      type="button"
      class="absolute right-3 top-3 rounded-sm opacity-70 hover:opacity-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
      aria-label="Close alert"
      @click="emit('close')"
    >
      <X class="size-4" aria-hidden="true" />
    </button>
  </div>
</template>
