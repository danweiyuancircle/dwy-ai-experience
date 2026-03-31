<script setup lang="ts">
import DemoBlock from '../components/DemoBlock.vue'
import ComponentDoc from '../components/ComponentDoc.vue'
import PropsTable from '../components/PropsTable.vue'
import EventsTable from '../components/EventsTable.vue'
import SlotsTable from '../components/SlotsTable.vue'

const slides = [
  { bg: 'bg-primary/20', text: '幻灯片 1 — 产品展示', sub: '展示您的最新产品' },
  { bg: 'bg-secondary/40', text: '幻灯片 2 — 特性介绍', sub: '了解核心功能' },
  { bg: 'bg-muted', text: '幻灯片 3 — 用户评价', sub: '来自真实用户的反馈' },
  { bg: 'bg-accent', text: '幻灯片 4 — 立即开始', sub: '快速上手指南' },
]

const tocItems = [
  { id: 'usage', label: '使用场景' },
  { id: 'basic', label: '基础轮播' },
  { id: 'autoplay', label: '自动播放' },
  { id: 'arrows-only', label: '仅箭头' },
  { id: 'props', label: 'Props' },
  { id: 'events', label: 'Events' },
  { id: 'slots', label: 'Slots' },
]

const propsData = [
  { name: 'loop', type: 'boolean', default: 'false', description: '是否循环播放' },
  { name: 'direction', type: "'horizontal' | 'vertical'", default: "'horizontal'", description: '轮播方向' },
  { name: 'showArrows', type: 'boolean', default: 'false', description: '是否显示左右导航箭头' },
  { name: 'showDots', type: 'boolean', default: 'false', description: '是否显示底部指示点' },
  { name: 'autoplay', type: 'boolean', default: 'false', description: '是否自动播放' },
  { name: 'interval', type: 'number', default: '3000', description: '自动播放间隔时间（毫秒）' },
  { name: 'class', type: 'string', default: '-', description: '自定义 CSS 类名' },
]

const eventsData = [
  { name: 'change', params: '(index: number)', description: '幻灯片切换时触发，返回当前索引' },
]

const slotsData = [
  { name: 'default', description: '轮播内容，放置 ECarouselItem 子组件' },
]
</script>

<template>
  <ComponentDoc
    title="Carousel 走马灯"
    description="轮播图组件，支持自动播放、显示箭头/点、水平/垂直方向。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">适用于首页 Banner 轮播、产品图片展示、公告信息滚动等需要在有限空间内展示多条内容的场景。支持自动播放、循环播放、导航箭头和指示点，可通过 direction 切换水平/垂直方向。</p>
    </section>

    <section id="basic">
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
    </section>

    <section id="autoplay">
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
    </section>

    <section id="arrows-only">
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
    </section>

    <section id="props">
      <PropsTable :data="propsData" />
    </section>

    <section id="events">
      <EventsTable :data="eventsData" />
    </section>

    <section id="slots">
      <SlotsTable :data="slotsData" />
    </section>
  </ComponentDoc>
</template>
