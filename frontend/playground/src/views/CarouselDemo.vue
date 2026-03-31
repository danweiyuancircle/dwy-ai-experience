<script setup lang="ts">
import DemoBlock from '../components/DemoBlock.vue'

const slides = [
  { bg: 'bg-primary/20', text: '幻灯片 1 — 产品展示', sub: '展示您的最新产品' },
  { bg: 'bg-secondary/40', text: '幻灯片 2 — 特性介绍', sub: '了解核心功能' },
  { bg: 'bg-muted', text: '幻灯片 3 — 用户评价', sub: '来自真实用户的反馈' },
  { bg: 'bg-accent', text: '幻灯片 4 — 立即开始', sub: '快速上手指南' },
]
</script>

<template>
  <div class="max-w-3xl">
    <h1 class="text-2xl font-bold mb-2">Carousel 走马灯</h1>
    <p class="text-muted-foreground mb-6">轮播图组件，支持自动播放、显示箭头/点、水平/垂直方向。</p>

    <DemoBlock
      title="基础轮播"
      description="带箭头和指示点的基础轮播"
      code='<ECarousel showArrows showDots>
  <ECarouselItem v-for="slide in slides" :key="slide.text">
    <div class="h-48 flex items-center justify-center">{{ slide.text }}</div>
  </ECarouselItem>
</ECarousel>'
    >
      <ECarousel :showArrows="true" :showDots="true">
        <ECarouselItem v-for="slide in slides" :key="slide.text">
          <div :class="['h-48 flex flex-col items-center justify-center rounded-md', slide.bg]">
            <p class="font-semibold text-lg">{{ slide.text }}</p>
            <p class="text-sm text-muted-foreground mt-1">{{ slide.sub }}</p>
          </div>
        </ECarouselItem>
      </ECarousel>
    </DemoBlock>

    <DemoBlock
      title="自动播放"
      description="设置 autoplay 和 interval 启用自动轮播"
      code='<ECarousel autoplay :interval="3000" showDots loop>'
    >
      <ECarousel :autoplay="true" :interval="2000" :showDots="true" :loop="true" :showArrows="true">
        <ECarouselItem v-for="slide in slides" :key="slide.text">
          <div :class="['h-40 flex items-center justify-center rounded-md', slide.bg]">
            <p class="font-semibold">{{ slide.text }}</p>
          </div>
        </ECarouselItem>
      </ECarousel>
    </DemoBlock>

    <DemoBlock
      title="仅箭头（无指示点）"
      description="只显示左右导航箭头"
    >
      <ECarousel :showArrows="true" :showDots="false">
        <ECarouselItem v-for="slide in slides" :key="slide.text">
          <div :class="['h-36 flex items-center justify-center rounded-md', slide.bg]">
            <p class="font-semibold">{{ slide.text }}</p>
          </div>
        </ECarouselItem>
      </ECarousel>
    </DemoBlock>
  </div>
</template>
