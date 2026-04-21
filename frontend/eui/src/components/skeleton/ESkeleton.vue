<!--
  ESkeleton 骨架屏占位
  加载中显示的灰色占位块，通过外部 class 控制尺寸与形状
  内置 animate-pulse 呼吸动画，降低等待感
-->
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
