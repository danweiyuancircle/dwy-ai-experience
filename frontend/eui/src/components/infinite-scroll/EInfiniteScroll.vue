<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import { LoaderCircle } from 'lucide-vue-next'
import { cn } from '@/utils/cn'
import type { EInfiniteScrollProps, EInfiniteScrollEmits } from './types'

const props = withDefaults(defineProps<EInfiniteScrollProps>(), {
  loading: false,
  disabled: false,
  distance: 0,
})

const emit = defineEmits<EInfiniteScrollEmits>()

const sentinelRef = ref<HTMLElement | null>(null)
let observer: IntersectionObserver | null = null

function setupObserver() {
  if (observer) observer.disconnect()
  if (!sentinelRef.value || props.disabled) return

  observer = new IntersectionObserver(
    (entries) => {
      const entry = entries[0]
      if (entry.isIntersecting && !props.loading && !props.disabled) {
        emit('load')
      }
    },
    {
      rootMargin: `0px 0px ${props.distance}px 0px`,
      threshold: 0,
    }
  )
  observer.observe(sentinelRef.value)
}

onMounted(() => {
  setupObserver()
})

watch(() => props.disabled, () => {
  setupObserver()
})

onBeforeUnmount(() => {
  observer?.disconnect()
})
</script>

<template>
  <div :class="cn('relative', props.class)">
    <slot />
    <div ref="sentinelRef" class="w-full">
      <div
        v-if="props.loading"
        class="flex items-center justify-center py-4 text-sm text-muted-foreground gap-2"
      >
        <LoaderCircle class="size-4 animate-spin" />
        <slot name="loading">Loading...</slot>
      </div>
      <div
        v-else-if="props.disabled"
        class="flex items-center justify-center py-4 text-sm text-muted-foreground"
      >
        <slot name="complete">No more data</slot>
      </div>
    </div>
  </div>
</template>
