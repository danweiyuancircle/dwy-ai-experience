<script setup lang="ts">
import { ref, computed } from 'vue'
import { Star } from 'lucide-vue-next'
import { cn } from '@/utils/cn'
import type { ERateProps, ERateEmits } from './types'

const props = withDefaults(defineProps<ERateProps>(), {
  modelValue: 0,
  max: 5,
  disabled: false,
  allowHalf: false,
  showText: false,
})

const emit = defineEmits<ERateEmits>()

const hoverValue = ref(-1)

const displayValue = computed(() =>
  hoverValue.value >= 0 ? hoverValue.value : (props.modelValue ?? 0)
)

function starFill(index: number): 'full' | 'half' | 'empty' {
  const val = displayValue.value
  if (val >= index + 1) return 'full'
  if (props.allowHalf && val >= index + 0.5) return 'half'
  return 'empty'
}

function handleClick(index: number, isHalf: boolean) {
  if (props.disabled) return
  const value = props.allowHalf && isHalf ? index + 0.5 : index + 1
  emit('update:modelValue', value)
  emit('change', value)
}

function handleMouseMove(event: MouseEvent, index: number) {
  if (props.disabled) return
  const rect = (event.currentTarget as HTMLElement).getBoundingClientRect()
  const isHalf = props.allowHalf && (event.clientX - rect.left) < rect.width / 2
  hoverValue.value = isHalf ? index + 0.5 : index + 1
}

function handleMouseLeave() {
  hoverValue.value = -1
}
</script>

<template>
  <div
    :class="cn('flex items-center gap-1', props.disabled && 'opacity-60 cursor-not-allowed', props.class)"
    @mouseleave="handleMouseLeave"
  >
    <button
      v-for="index in props.max"
      :key="index"
      type="button"
      :disabled="props.disabled"
      class="relative p-0.5 focus:outline-none disabled:cursor-not-allowed"
      @mousemove="handleMouseMove($event, index - 1)"
      @click="handleClick(index - 1, props.allowHalf && hoverValue === index - 0.5)"
    >
      <span class="relative inline-flex size-5">
        <!-- Base star (always rendered) -->
        <Star class="size-5" :class="starFill(index - 1) === 'full' ? 'fill-yellow-400 text-yellow-400' : 'text-muted-foreground'" />
        <!-- Half overlay -->
        <span v-if="starFill(index - 1) === 'half'" class="absolute inset-0 overflow-hidden w-1/2">
          <Star class="size-5 fill-yellow-400 text-yellow-400" />
        </span>
      </span>
    </button>
    <span v-if="props.showText" class="ml-2 text-sm text-muted-foreground">
      {{ displayValue }} / {{ props.max }}
    </span>
  </div>
</template>
