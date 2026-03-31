<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue'
import { cn } from '@/utils/cn'
import type { EWatermarkProps } from './types'

const props = withDefaults(defineProps<EWatermarkProps>(), {
  content: 'Watermark',
  fontSize: 14,
  rotate: -30,
  gap: () => [100, 100],
  opacity: 0.15,
})

const dataUrl = ref('')

function generateWatermark() {
  const canvas = document.createElement('canvas')
  const texts = Array.isArray(props.content) ? props.content : [props.content]
  const gap = props.gap ?? [100, 100]
  const fontSize = props.fontSize ?? 14
  const rotate = (props.rotate ?? -30) * (Math.PI / 180)

  // Measure text width
  const ctx = canvas.getContext('2d')!
  ctx.font = `${fontSize}px sans-serif`
  const maxWidth = Math.max(...texts.map(t => ctx.measureText(t).width))

  const tileWidth = maxWidth + gap[0]
  const tileHeight = texts.length * (fontSize + 4) + gap[1]

  canvas.width = tileWidth
  canvas.height = tileHeight

  const ctx2 = canvas.getContext('2d')!
  ctx2.globalAlpha = props.opacity ?? 0.15
  ctx2.font = `${fontSize}px sans-serif`
  ctx2.fillStyle = 'rgba(0,0,0,0.5)'
  ctx2.textAlign = 'center'
  ctx2.textBaseline = 'middle'

  ctx2.translate(tileWidth / 2, tileHeight / 2)
  ctx2.rotate(rotate)

  texts.forEach((text, i) => {
    const y = (i - (texts.length - 1) / 2) * (fontSize + 4)
    ctx2.fillText(text ?? '', 0, y)
  })

  dataUrl.value = canvas.toDataURL()
}

onMounted(() => {
  generateWatermark()
})

watch(
  () => [props.content, props.fontSize, props.rotate, props.gap, props.opacity],
  () => generateWatermark(),
  { deep: true }
)
</script>

<template>
  <div :class="cn('relative', props.class)">
    <slot />
    <div
      v-if="dataUrl"
      class="absolute inset-0 pointer-events-none"
      :style="{
        backgroundImage: `url(${dataUrl})`,
        backgroundRepeat: 'repeat',
        zIndex: 9,
      }"
    />
  </div>
</template>
