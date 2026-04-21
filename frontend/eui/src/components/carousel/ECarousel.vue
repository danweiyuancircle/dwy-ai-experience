<!--
  ECarousel 走马灯组件
  基于 embla-carousel-vue 封装，提供箭头、指示点、自动轮播、键盘导航
  鼠标悬停自动暂停；子项使用 ECarouselItem 包裹
-->
<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { ChevronLeft, ChevronRight } from 'lucide-vue-next'
import emblaCarouselVue, { type EmblaCarouselVueType } from 'embla-carousel-vue'
import { cn } from '@/utils/cn'
import type { ECarouselProps, ECarouselEmits } from './types'

const props = withDefaults(defineProps<ECarouselProps>(), {
  loop: false,
  direction: 'horizontal',
  showArrows: true,
  showDots: true,
  autoplay: false,
  interval: 3000,
})

const emit = defineEmits<ECarouselEmits>()

const [emblaRef, emblaApi]: EmblaCarouselVueType = emblaCarouselVue({
  loop: props.loop,
  axis: props.direction === 'vertical' ? 'y' : 'x',
})

const canScrollPrev = ref(false)
const canScrollNext = ref(false)
const currentIndex = ref(0)
const slideCount = ref(0)

/**
 * 同步 embla 内部状态到响应式变量并派发 change 事件
 */
function onSelect() {
  if (!emblaApi.value) return
  canScrollPrev.value = emblaApi.value.canScrollPrev()
  canScrollNext.value = emblaApi.value.canScrollNext()
  currentIndex.value = emblaApi.value.selectedScrollSnap()
  emit('change', currentIndex.value)
}

/** 切换到上一张 */
function scrollPrev() {
  emblaApi.value?.scrollPrev()
}

/** 切换到下一张 */
function scrollNext() {
  emblaApi.value?.scrollNext()
}

/** 跳转到指定索引 */
function scrollTo(index: number) {
  emblaApi.value?.scrollTo(index)
}

let autoplayTimer: ReturnType<typeof setInterval> | null = null

/**
 * 启动自动轮播：到末尾时根据 loop 决定是否回到首张
 */
function startAutoplay() {
  if (!props.autoplay) return
  autoplayTimer = setInterval(() => {
    if (!emblaApi.value) return
    if (emblaApi.value.canScrollNext()) {
      emblaApi.value.scrollNext()
    } else if (props.loop) {
      emblaApi.value.scrollTo(0)
    }
  }, props.interval)
}

/**
 * 停止自动轮播计时器
 */
function stopAutoplay() {
  if (autoplayTimer) {
    clearInterval(autoplayTimer)
    autoplayTimer = null
  }
}

onMounted(() => {
  if (!emblaApi.value) return
  slideCount.value = emblaApi.value.slideNodes().length
  emblaApi.value.on('init', onSelect)
  emblaApi.value.on('reInit', onSelect)
  emblaApi.value.on('select', onSelect)
  onSelect()
  startAutoplay()
})

onBeforeUnmount(() => {
  stopAutoplay()
})

// autoplay prop 动态切换时重启/关闭计时器
watch(() => props.autoplay, (val) => {
  if (val) startAutoplay()
  else stopAutoplay()
})

/**
 * 键盘事件：根据方向决定左右箭头或上下箭头切换
 */
function onKeyDown(event: KeyboardEvent) {
  const prevKey = props.direction === 'vertical' ? 'ArrowUp' : 'ArrowLeft'
  const nextKey = props.direction === 'vertical' ? 'ArrowDown' : 'ArrowRight'
  if (event.key === prevKey) { event.preventDefault(); scrollPrev() }
  if (event.key === nextKey) { event.preventDefault(); scrollNext() }
}

// 将 emblaApi 以 unknown 暴露，避免声明文件中出现不可移植的 pnpm 路径
defineExpose({ scrollPrev, scrollNext, scrollTo, emblaApi: emblaApi as unknown })
</script>

<template>
  <div
    data-slot="carousel"
    :class="cn('relative', props.class)"
    role="region"
    aria-roledescription="carousel"
    tabindex="0"
    @keydown="onKeyDown"
    @mouseenter="stopAutoplay"
    @mouseleave="startAutoplay"
  >
    <!-- Viewport -->
    <div ref="emblaRef" class="overflow-hidden">
      <div
        :class="cn(
          'flex',
          direction === 'horizontal' ? '-ml-4' : '-mt-4 flex-col',
        )"
      >
        <slot />
      </div>
    </div>

    <!-- Arrow buttons -->
    <template v-if="showArrows">
      <button
        :disabled="!canScrollPrev"
        :class="cn(
          'absolute size-8 rounded-full border border-input bg-background shadow-sm flex items-center justify-center',
          'disabled:pointer-events-none disabled:opacity-50',
          'hover:bg-accent hover:text-accent-foreground',
          direction === 'horizontal'
            ? 'top-1/2 -left-4 -translate-y-1/2'
            : '-top-4 left-1/2 -translate-x-1/2',
        )"
        aria-label="Previous slide"
        @click="scrollPrev"
      >
        <ChevronLeft class="size-4" />
      </button>
      <button
        :disabled="!canScrollNext"
        :class="cn(
          'absolute size-8 rounded-full border border-input bg-background shadow-sm flex items-center justify-center',
          'disabled:pointer-events-none disabled:opacity-50',
          'hover:bg-accent hover:text-accent-foreground',
          direction === 'horizontal'
            ? 'top-1/2 -right-4 -translate-y-1/2'
            : '-bottom-4 left-1/2 -translate-x-1/2',
        )"
        aria-label="Next slide"
        @click="scrollNext"
      >
        <ChevronRight class="size-4" />
      </button>
    </template>

    <!-- Dots -->
    <div
      v-if="showDots && slideCount > 1"
      :class="cn(
        'absolute flex gap-1',
        direction === 'horizontal'
          ? 'bottom-2 left-1/2 -translate-x-1/2 flex-row'
          : 'right-2 top-1/2 -translate-y-1/2 flex-col',
      )"
    >
      <button
        v-for="i in slideCount"
        :key="i"
        :class="cn(
          'rounded-full transition-all',
          currentIndex === i - 1
            ? 'bg-primary size-2'
            : 'bg-primary/40 size-1.5',
        )"
        :aria-label="`Go to slide ${i}`"
        @click="scrollTo(i - 1)"
      />
    </div>
  </div>
</template>
