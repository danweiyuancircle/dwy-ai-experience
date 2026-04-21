<!--
  ESlider 滑动条组件
  基于 reka-ui Slider 封装，modelValue 为数组以支持单/双滑块（范围选择）
  单滑块传 [50]，双滑块传 [20, 80]
-->
<script setup lang="ts">
import { SliderRoot, SliderTrack, SliderRange, SliderThumb } from 'reka-ui'
import { cn } from '@/utils/cn'
import type { ESliderProps, ESliderEmits } from './types'

const props = withDefaults(defineProps<ESliderProps>(), {
  min: 0,
  max: 100,
  step: 1,
  disabled: false,
  orientation: 'horizontal',
})

const emit = defineEmits<ESliderEmits>()
</script>

<template>
  <SliderRoot
    data-slot="slider"
    :model-value="props.modelValue"
    :min="props.min"
    :max="props.max"
    :step="props.step"
    :disabled="props.disabled"
    :orientation="props.orientation"
    :class="cn(
      'relative flex touch-none select-none data-[disabled]:opacity-50',
      props.orientation === 'vertical' ? 'h-full flex-col items-center' : 'w-full items-center',
      props.class,
    )"
    @update:model-value="(val) => val !== undefined && emit('update:modelValue', val)"
  >
    <SliderTrack
      data-slot="slider-track"
      class="bg-muted relative grow overflow-hidden rounded-full data-[orientation=horizontal]:h-1.5 data-[orientation=horizontal]:w-full data-[orientation=vertical]:w-1.5 data-[orientation=vertical]:h-full"
    >
      <SliderRange
        data-slot="slider-range"
        class="bg-primary absolute data-[orientation=horizontal]:h-full data-[orientation=vertical]:w-full"
      />
    </SliderTrack>
    <SliderThumb
      v-for="(_, key) in (props.modelValue ?? [0])"
      :key="key"
      data-slot="slider-thumb"
      class="bg-white border-primary ring-ring/50 block size-4 shrink-0 rounded-full border shadow-sm transition-[color,box-shadow] hover:ring-4 focus-visible:ring-4 focus-visible:outline-hidden disabled:pointer-events-none disabled:opacity-50"
    />
  </SliderRoot>
</template>
