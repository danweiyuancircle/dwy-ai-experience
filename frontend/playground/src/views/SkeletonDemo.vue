<script setup lang="ts">
import { ref } from 'vue'
import DemoBlock from '../components/DemoBlock.vue'

const loading = ref(true)
</script>

<template>
  <div class="max-w-3xl">
    <h1 class="text-2xl font-bold mb-2">Skeleton 骨架屏</h1>
    <p class="text-muted-foreground mb-6">加载占位组件，在内容加载过程中提供视觉反馈，减少感知延迟。</p>

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
  </div>
</template>
