<script setup lang="ts">
import { ref } from 'vue'
import DemoBlock from '../components/DemoBlock.vue'
import ComponentDoc from '../components/ComponentDoc.vue'
import PropsTable from '../components/PropsTable.vue'
import EventsTable from '../components/EventsTable.vue'
import SlotsTable from '../components/SlotsTable.vue'

const items = ref<string[]>([])
const isLoading = ref(false)
const isDisabled = ref(false)
let page = 0
const totalPages = 5

function initItems() {
  items.value = Array.from({ length: 10 }, (_, i) => `项目 ${i + 1}`)
  page = 1
  isDisabled.value = false
}
initItems()

function handleLoad() {
  if (isLoading.value || isDisabled.value) return
  isLoading.value = true
  setTimeout(() => {
    page++
    const start = items.value.length
    const newItems = Array.from({ length: 10 }, (_, i) => `项目 ${start + i + 1}`)
    items.value.push(...newItems)
    isLoading.value = false
    if (page >= totalPages) {
      isDisabled.value = true
    }
  }, 1000)
}

const tocItems = [
  { id: 'usage', label: '使用场景' },
  { id: 'basic', label: '基础用法' },
  { id: 'distance', label: '触发距离' },
  { id: 'props', label: 'Props' },
  { id: 'events', label: 'Events' },
  { id: 'slots', label: 'Slots' },
]

const propsData = [
  { name: 'loading', type: 'boolean', default: 'false', description: '是否处于加载状态' },
  { name: 'disabled', type: 'boolean', default: 'false', description: '是否禁用（到底时停止触发）' },
  { name: 'distance', type: 'number', default: '0', description: '触发加载的底部距离（px）' },
  { name: 'class', type: 'string', description: '自定义 CSS 类名' },
]

const eventsData = [
  { name: 'load', params: '()', description: '滚动到底部时触发，用于加载更多数据' },
]

const slotsData = [
  { name: 'default', description: '列表内容' },
  { name: 'loading', description: '自定义加载中提示' },
  { name: 'complete', description: '自定义加载完成提示' },
]
</script>

<template>
  <ComponentDoc
    title="InfiniteScroll 无限滚动"
    description="当滚动到底部时自动加载更多数据，适用于长列表的分页加载场景。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">适用于内容流式展示的场景，如消息列表、商品列表、动态信息流等。用户无需手动翻页，滚动到底部即自动加载下一页数据，提升浏览体验。</p>
    </section>

    <section id="basic">
      <DemoBlock
        title="基础用法"
        description="滚动到列表底部自动触发加载，加载完成后自动停止"
        code='<EInfiniteScroll
  :loading="isLoading"
  :disabled="isDisabled"
  @load="handleLoad"
>
  <div v-for="item in items" :key="item">{{ item }}</div>
  <template #loading>加载中...</template>
  <template #complete>已加载全部数据</template>
</EInfiniteScroll>'
      >
        <div class="h-64 overflow-y-auto rounded-lg border">
          <EInfiniteScroll
            :loading="isLoading"
            :disabled="isDisabled"
            @load="handleLoad"
          >
            <div class="divide-y">
              <div
                v-for="item in items"
                :key="item"
                class="px-4 py-3 text-sm hover:bg-muted/50 transition-colors"
              >
                {{ item }}
              </div>
            </div>
            <template #loading>
              <span>加载中...</span>
            </template>
            <template #complete>
              <span>已加载全部 {{ items.length }} 条数据</span>
            </template>
          </EInfiniteScroll>
        </div>
        <div class="mt-2 flex items-center gap-3">
          <span class="text-xs text-muted-foreground">已加载 {{ items.length }} 条，共 {{ totalPages }} 页</span>
          <EButton variant="outline" size="sm" @click="initItems()">重置列表</EButton>
        </div>
      </DemoBlock>
    </section>

    <section id="distance">
      <DemoBlock
        title="触发距离"
        description="distance 属性设置提前触发加载的距离（px），可实现预加载效果"
        code='<EInfiniteScroll :distance="100" :loading="loading" @load="handleLoad">
  <!-- 距离底部 100px 时就开始加载 -->
</EInfiniteScroll>'
      >
        <p class="text-sm text-muted-foreground">设置 <code class="text-xs bg-muted px-1.5 py-0.5 rounded">distance="100"</code> 后，滚动到距底部 100px 处即触发加载，给用户更流畅的体验。此属性通过 IntersectionObserver 的 rootMargin 实现。</p>
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
