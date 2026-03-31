<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, computed } from 'vue'
import { cn } from '@/utils/cn'
import type { EAffixProps } from './types'

const props = withDefaults(defineProps<EAffixProps>(), {
  offset: 0,
  position: 'top',
})

const isFixed = ref(false)
const affixRef = ref<HTMLElement | null>(null)
const placeholderRef = ref<HTMLElement | null>(null)
const placeholderHeight = ref(0)

function handleScroll() {
  if (!affixRef.value) return

  if (!isFixed.value) {
    placeholderHeight.value = affixRef.value.offsetHeight
  }

  const domRect = affixRef.value.getBoundingClientRect()

  if (props.position === 'top') {
    isFixed.value = domRect.top <= (props.offset ?? 0)
  } else {
    isFixed.value = domRect.bottom >= window.innerHeight - (props.offset ?? 0)
  }
}

const fixedStyle = computed(() => {
  if (!isFixed.value) return {}
  return props.position === 'top'
    ? { position: 'fixed' as const, top: `${props.offset}px`, zIndex: 100 }
    : { position: 'fixed' as const, bottom: `${props.offset}px`, zIndex: 100 }
})

onMounted(() => {
  window.addEventListener('scroll', handleScroll, { passive: true })
  handleScroll()
})

onBeforeUnmount(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>

<template>
  <div ref="placeholderRef" :style="isFixed ? { height: `${placeholderHeight}px` } : {}">
    <div
      ref="affixRef"
      :class="cn(props.class)"
      :style="fixedStyle"
    >
      <slot />
    </div>
  </div>
</template>
