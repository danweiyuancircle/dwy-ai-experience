<script setup lang="ts">
import { Transition } from 'vue'
import type { ETransitionProps } from './types'

withDefaults(defineProps<ETransitionProps>(), { preset: 'fade' })
</script>

<template>
  <Transition :name="'eui-' + preset" :appear="appear">
    <slot />
  </Transition>
</template>
