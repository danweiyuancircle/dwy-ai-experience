<!--
  ECarouselItem 走马灯子项组件
  必须作为 ECarousel 的子节点使用，提供统一的宽度与留白
-->
<script setup lang="ts">
import type { HTMLAttributes } from 'vue'
import { cn } from '@/utils/cn'

const props = defineProps<{
  /** 自定义 class，透传到根元素 */
  class?: HTMLAttributes['class']
}>()
</script>

<template>
  <div
    data-slot="carousel-item"
    role="group"
    aria-roledescription="slide"
    :class="cn('min-w-0 shrink-0 grow-0 basis-full pl-4', props.class)"
  >
    <slot />
  </div>
</template>
