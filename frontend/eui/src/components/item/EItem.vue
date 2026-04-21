<!--
  EItem 列表项通用容器组件
  基于 reka-ui Primitive 渲染，提供统一的圆角、边框、间距的单行容器
-->
<script setup lang="ts">
import { Primitive } from 'reka-ui'
import { cn } from '@/utils/cn'
import { itemVariants } from './types'
import type { EItemProps } from './types'

const props = withDefaults(defineProps<EItemProps>(), {
  as: 'div',
})
</script>

<template>
  <Primitive
    data-slot="item"
    :as="props.as"
    :class="cn(itemVariants({ variant: props.variant, size: props.size }), props.class)"
  >
    <slot />
  </Primitive>
</template>
