<!--
  EImage 图片组件
  支持懒加载（IntersectionObserver）、加载失败 fallback、点击大图预览
  Loading 骨架屏在加载完成后自动淡出
-->
<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { ImageOff, ZoomIn, X } from 'lucide-vue-next'
import { cn } from '@/utils/cn'
import type { EImageProps } from './types'

const props = withDefaults(defineProps<EImageProps>(), {
  fit: 'cover',
  lazy: false,
  preview: false,
})

const imageRef = ref<HTMLImageElement | null>(null)
const containerRef = ref<HTMLDivElement | null>(null)
const loaded = ref(false)
const error = ref(false)
// 非懒加载模式默认可见，懒加载需等进入视口才置为 true
const visible = ref(!props.lazy)
const previewOpen = ref(false)

let observer: IntersectionObserver | null = null

onMounted(() => {
  if (!props.lazy) {
    visible.value = true
    return
  }
  if (!containerRef.value) return
  // 懒加载：进入视口 10% 触发加载后断开观察
  observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          visible.value = true
          observer?.disconnect()
        }
      })
    },
    { threshold: 0.1 },
  )
  observer.observe(containerRef.value)
})

onBeforeUnmount(() => {
  observer?.disconnect()
})

/** 图片 load 事件处理 */
function onLoad() {
  loaded.value = true
  error.value = false
}

/** 图片 error 事件处理 */
function onError() {
  error.value = true
  loaded.value = false
}

// 将 fit prop 映射为 Tailwind object-fit 工具类
const objectFitClass = computed(() => {
  const map: Record<string, string> = {
    contain: 'object-contain',
    cover: 'object-cover',
    fill: 'object-fill',
    none: 'object-none',
    'scale-down': 'object-scale-down',
  }
  return map[props.fit ?? 'cover'] ?? 'object-cover'
})

/** 打开大图预览：仅在 preview 开启且已加载成功时生效 */
function openPreview() {
  if (props.preview && loaded.value) {
    previewOpen.value = true
  }
}

/** 关闭大图预览 */
function closePreview() {
  previewOpen.value = false
}
</script>

<template>
  <div
    ref="containerRef"
    data-slot="image"
    :class="cn('group relative overflow-hidden inline-flex items-center justify-center bg-muted', props.class)"
  >
    <!-- Lazy placeholder / loading skeleton -->
    <div
      v-if="!loaded && !error"
      class="absolute inset-0 animate-pulse bg-muted"
    />

    <!-- Actual image -->
    <img
      v-if="visible && src && !error"
      ref="imageRef"
      :src="src"
      :alt="alt"
      :class="cn(
        'w-full h-full transition-opacity duration-300',
        objectFitClass,
        loaded ? 'opacity-100' : 'opacity-0',
        preview && loaded ? 'cursor-zoom-in' : '',
      )"
      @load="onLoad"
      @error="onError"
      @click="openPreview"
    />

    <!-- Fallback image -->
    <img
      v-else-if="error && fallback"
      :src="fallback"
      :alt="alt"
      :class="cn('w-full h-full', objectFitClass)"
    />

    <!-- Error placeholder -->
    <div
      v-else-if="error && !fallback"
      class="flex flex-col items-center justify-center gap-1 text-muted-foreground/50 w-full h-full"
    >
      <ImageOff class="size-8" />
      <span class="text-xs">Image failed to load</span>
    </div>

    <!-- Preview zoom indicator -->
    <div
      v-if="preview && loaded"
      class="absolute inset-0 flex items-center justify-center bg-black/0 hover:bg-black/20 transition-colors cursor-zoom-in"
      @click="openPreview"
    >
      <ZoomIn class="size-6 text-white opacity-0 group-hover:opacity-100 transition-opacity" />
    </div>
  </div>

  <!-- Preview overlay -->
  <Teleport to="body">
    <div
      v-if="previewOpen"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/80"
      @click="closePreview"
    >
      <img
        :src="src"
        :alt="alt"
        class="max-h-[90vh] max-w-[90vw] object-contain rounded"
        @click.stop
      />
      <button
        class="absolute top-4 right-4 text-white/80 hover:text-white"
        aria-label="Close preview"
        @click="closePreview"
      >
        <X class="size-6" />
      </button>
    </div>
  </Teleport>
</template>
