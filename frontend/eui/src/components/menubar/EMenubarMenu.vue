<script setup lang="ts">
import { MenubarMenu } from 'reka-ui'
import type { EMenubarMenuProps } from './types'

const props = defineProps<EMenubarMenuProps>()
</script>

<template>
  <MenubarMenu :value="props.value">
    <slot />
  </MenubarMenu>
</template>
