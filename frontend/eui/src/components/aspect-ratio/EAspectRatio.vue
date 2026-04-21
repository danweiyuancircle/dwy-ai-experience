<!--
  EAspectRatio 固定宽高比容器组件
  基于 reka-ui AspectRatio 原语封装，默认 16:9 比例
  放置图片、视频、iframe 等媒体内容保持等比缩放
-->
<script setup lang="ts">
import { AspectRatio } from 'reka-ui'
import type { EAspectRatioProps } from './types'

const props = withDefaults(defineProps<EAspectRatioProps>(), {
  ratio: 16 / 9,
})
</script>

<template>
  <AspectRatio
    data-slot="aspect-ratio"
    :ratio="props.ratio"
    :class="props.class"
  >
    <slot />
  </AspectRatio>
</template>
