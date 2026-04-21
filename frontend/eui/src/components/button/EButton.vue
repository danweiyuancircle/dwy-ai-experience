<!--
  EButton 按钮组件
  基于 reka-ui Primitive 封装，支持 variant / size / loading / disabled
  loading 态下自动禁用点击并展示旋转图标
-->
<script setup lang="ts">
import { Primitive } from 'reka-ui'
import { LoaderCircle } from 'lucide-vue-next'
import { cn } from '@/utils/cn'
import { buttonVariants } from './types'
import type { EButtonProps } from './types'

const props = withDefaults(defineProps<EButtonProps>(), {
  as: 'button',
  disabled: false,
  loading: false,
})
</script>

<template>
  <Primitive
    data-slot="button"
    :data-variant="variant"
    :data-size="size"
    :as="as"
    :as-child="asChild"
    :disabled="disabled || loading"
    :class="cn(buttonVariants({ variant, size }), props.class)"
  >
    <LoaderCircle v-if="loading" class="size-4 animate-spin" aria-hidden="true" />
    <slot />
  </Primitive>
</template>
