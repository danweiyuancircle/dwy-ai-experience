<script setup lang="ts">
import { ref } from 'vue'
import DemoBlock from '../components/DemoBlock.vue'
import ComponentDoc from '../components/ComponentDoc.vue'
import PropsTable from '../components/PropsTable.vue'

const loading = ref(true)

const tocItems = [
  { id: 'usage', label: '使用场景' },
  { id: 'basic', label: '基础骨架块' },
  { id: 'avatar', label: '头像 + 文字骨架' },
  { id: 'card', label: '卡片骨架' },
  { id: 'toggle', label: '交互式切换' },
  { id: 'props', label: 'Props' },
]

const propsData = [
  { name: 'class', type: 'string', default: '-', description: '自定义 CSS 类名（通过 Tailwind 控制尺寸和圆角）' },
]
</script>

<template>
  <ComponentDoc
    title="Skeleton 骨架屏"
    description="加载占位组件，在内容加载过程中提供视觉反馈，减少感知延迟。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">适用于页面初始加载或异步数据请求期间，以占位块模拟真实内容的布局形状，减少用户等待焦虑。通过 Tailwind 类名控制骨架块的宽高、圆角等样式，灵活组合出文本行、头像、卡片等常见加载骨架。</p>
    </section>

    <section id="basic">
      <DemoBlock
        title="基础骨架块"
        description="不同尺寸的骨架占位块"
        code='<ESkeleton class="h-4 w-full" />
<ESkeleton class="h-4 w-3/4" />
<ESkeleton class="h-4 w-1/2" />'
      >
        <div class="space-y-2 max-w-sm">
          <ESkeleton class="h-4 w-full" />
          <ESkeleton class="h-4 w-3/4" />
          <ESkeleton class="h-4 w-1/2" />
          <ESkeleton class="h-4 w-2/3" />
        </div>
      </DemoBlock>
    </section>

    <section id="avatar">
      <DemoBlock
        title="头像 + 文字骨架"
        description="模拟用户卡片的加载状态"
        code='<div class="flex items-center gap-4">
  <ESkeleton class="size-12 rounded-full" />
  <div class="space-y-2 flex-1">
    <ESkeleton class="h-4 w-32" />
    <ESkeleton class="h-3 w-24" />
  </div>
</div>'
      >
        <div class="space-y-4 max-w-sm">
          <div v-for="i in 3" :key="i" class="flex items-center gap-4">
            <ESkeleton class="size-10 rounded-full" />
            <div class="space-y-2 flex-1">
              <ESkeleton class="h-4 w-32" />
              <ESkeleton class="h-3 w-24" />
            </div>
          </div>
        </div>
      </DemoBlock>
    </section>

    <section id="card">
      <DemoBlock
        title="卡片骨架"
        description="模拟内容卡片的加载状态"
      >
        <div class="border rounded-lg p-4 space-y-4 max-w-sm">
          <ESkeleton class="h-40 w-full rounded-md" />
          <div class="space-y-2">
            <ESkeleton class="h-5 w-3/4" />
            <ESkeleton class="h-4 w-full" />
            <ESkeleton class="h-4 w-5/6" />
            <ESkeleton class="h-4 w-2/3" />
          </div>
          <div class="flex gap-2">
            <ESkeleton class="h-9 w-20" />
            <ESkeleton class="h-9 w-20" />
          </div>
        </div>
      </DemoBlock>
    </section>

    <section id="toggle">
      <DemoBlock
        title="交互式切换"
        description="模拟真实的加载切换场景"
      >
        <div class="space-y-4">
          <ESwitch v-model="loading" label="显示骨架屏（模拟加载中）" />
          <div class="border rounded-lg p-4 max-w-sm">
            <div v-if="loading" class="space-y-3">
              <ESkeleton class="h-5 w-1/2" />
              <ESkeleton class="h-4 w-full" />
              <ESkeleton class="h-4 w-3/4" />
              <div class="flex gap-2 mt-2">
                <ESkeleton class="h-8 w-16" />
                <ESkeleton class="h-8 w-16" />
              </div>
            </div>
            <div v-else class="space-y-3">
              <h4 class="font-medium">加载完成</h4>
              <p class="text-sm text-muted-foreground">这是真实的内容，已成功从服务器加载。</p>
              <div class="flex gap-2">
                <EButton size="sm">编辑</EButton>
                <EButton size="sm" variant="outline">分享</EButton>
              </div>
            </div>
          </div>
        </div>
      </DemoBlock>
    </section>

    <section id="props">
      <PropsTable :data="propsData" />
    </section>
  </ComponentDoc>
</template>
