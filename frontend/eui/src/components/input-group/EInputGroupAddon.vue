<!--
  EInputGroupAddon 输入框附加块组件
  用于在 EInputGroup 内部放置前缀图标、单位、按钮等附加元素
  通过 align prop 控制位置（行内前后或独占一行的上下）
-->
<script setup lang="ts">
import { cn } from '@/utils/cn'
import { inputGroupAddonVariants } from './types'
import type { EInputGroupAddonProps } from './types'

const props = withDefaults(defineProps<EInputGroupAddonProps>(), {
  align: 'inline-start',
})
</script>

<template>
  <div
    role="group"
    data-slot="input-group-addon"
    :data-align="props.align"
    :class="cn(inputGroupAddonVariants({ align: props.align }), props.class)"
  >
    <slot />
  </div>
</template>
