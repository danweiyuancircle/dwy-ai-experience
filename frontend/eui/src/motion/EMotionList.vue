<script setup lang="ts" generic="T extends object">
import { usePreferredReducedMotion } from '@vueuse/core'
import { AnimatePresence, Motion } from 'motion-v'
import { onBeforeUpdate, onUpdated, ref } from 'vue'
import type { EMotionListProps } from './types'

const props = defineProps<EMotionListProps<T>>()

defineSlots<{
  default(props: { item: T; index: number }): unknown
}>()

const preference = usePreferredReducedMotion()
const list = ref<HTMLUListElement>()
let focused: HTMLElement | null = null

onBeforeUpdate(() => {
  const active = document.activeElement
  focused = active instanceof HTMLElement && list.value?.contains(active) ? active : null
})

onUpdated(() => {
  // DOM 移位可能使仍存在的节点丢焦，仅在没有其他目标接管焦点时恢复。
  if (focused?.isConnected && document.activeElement === document.body) {
    focused.focus({ preventScroll: true })
  }
  focused = null
})
</script>

<template>
  <ul ref="list" data-slot="motion-list">
    <AnimatePresence :initial="false">
      <Motion
        v-for="(item, index) in items"
        :key="item[props.itemKey] as string | number"
        as="li"
        :layout="preference === 'reduce' ? false : 'position'"
        :initial="preference === 'reduce' ? false : { opacity: 0 }"
        :animate="{ opacity: 1 }"
        :exit="preference === 'reduce' ? undefined : { opacity: 0 }"
        :transition="{ duration: preference === 'reduce' ? 0 : .18, ease: 'easeOut' }"
      >
        <slot :item="item" :index="index" />
      </Motion>
    </AnimatePresence>
  </ul>
</template>
