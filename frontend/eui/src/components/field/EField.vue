<!--
  EField 表单字段容器组件
  提供 label / control / description 的基础布局容器
  通过 data-invalid 驱动错误态样式，自身不参与表单校验
-->
<script setup lang="ts">
import { cn } from '@/utils/cn'
import { fieldVariants } from './types'
import type { EFieldProps } from './types'

const props = withDefaults(defineProps<EFieldProps>(), {
  orientation: 'vertical',
})
</script>

<template>
  <div
    role="group"
    data-slot="field"
    :data-orientation="props.orientation"
    :data-invalid="props.invalid"
    :class="cn(fieldVariants({ orientation: props.orientation }), props.class)"
  >
    <slot />
  </div>
</template>
