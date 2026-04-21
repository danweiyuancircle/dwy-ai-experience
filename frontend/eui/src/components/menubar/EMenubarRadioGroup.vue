<!--
  EMenubarRadioGroup 单选菜单组
  包裹多个 EMenubarRadioItem，通过 modelValue 标识当前选中项
-->
<script setup lang="ts">
import { MenubarRadioGroup } from 'reka-ui'
import { cn } from '@/utils/cn'
import type { EMenubarRadioGroupProps } from './types'

const props = defineProps<EMenubarRadioGroupProps>()
const emit = defineEmits<{
  /** 选中值变化 */
  (e: 'update:modelValue', val: string): void
}>()
</script>

<template>
  <MenubarRadioGroup
    :model-value="props.modelValue"
    :class="cn(props.class)"
    @update:model-value="emit('update:modelValue', $event as string)"
  >
    <slot />
  </MenubarRadioGroup>
</template>
