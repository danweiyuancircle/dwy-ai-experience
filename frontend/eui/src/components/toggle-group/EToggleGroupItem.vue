<!--
  EToggleGroupItem 开关按钮组子项
  桥接 reka-ui ToggleGroupItem，必须放在 EToggleGroup 内使用：
  由组 Root 收集各子项 value，single 模式下与组 modelValue 匹配的子项呈选中态。
  variant/size 缺省继承组注入值（provide/inject），并落到 data-* 属性供样式定制。
  注意：独立 EToggle 是布尔开关，不能替代本组件放进组内——无 value 概念，选中态无法联动。
-->
<script setup lang="ts">
import { inject } from 'vue'
import { ToggleGroupItem } from 'reka-ui'
import { cn } from '@/utils/cn'
import { toggleVariants } from '../toggle/types'
import type { EToggleGroupItemProps, EToggleGroupProps } from './types'

const props = withDefaults(defineProps<EToggleGroupItemProps>(), {
  disabled: false,
})

/** 组注入的 variant/size（EToggleGroup provide）；未在组内使用时回退到自身 props */
const group = inject<{ variant: { value?: EToggleGroupProps['variant'] }; size: { value?: EToggleGroupProps['size'] } }>(
  'toggleGroup',
  undefined,
)
const variant = group?.variant.value ?? props.variant
const size = group?.size.value ?? props.size
</script>

<template>
  <ToggleGroupItem
    data-slot="toggle-group-item"
    :data-variant="variant"
    :data-size="size"
    :value="props.value"
    :disabled="props.disabled"
    :class="cn(toggleVariants({ variant, size }), props.class)"
  >
    <slot />
  </ToggleGroupItem>
</template>
