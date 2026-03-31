<script setup lang="ts">
import { CollapsibleContent, CollapsibleRoot, CollapsibleTrigger } from 'reka-ui'
import { cn } from '@/utils/cn'
import type { ECollapsibleProps, ECollapsibleEmits } from './types'

const props = withDefaults(defineProps<ECollapsibleProps>(), {
  disabled: false,
})

const emit = defineEmits<ECollapsibleEmits>()

function onUpdate(value: boolean) {
  emit('update:modelValue', value)
}
</script>

<template>
  <CollapsibleRoot
    data-slot="collapsible"
    :open="modelValue"
    :disabled="disabled"
    :class="cn(props.class)"
    @update:open="onUpdate"
  >
    <CollapsibleTrigger data-slot="collapsible-trigger" as-child>
      <slot name="trigger" />
    </CollapsibleTrigger>
    <CollapsibleContent data-slot="collapsible-content">
      <slot />
    </CollapsibleContent>
  </CollapsibleRoot>
</template>
