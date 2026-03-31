<script setup lang="ts">
import { ref } from 'vue'
import { X, Plus, Settings, AlertTriangle, HelpCircle } from 'lucide-vue-next'
import DemoBlock from '../components/DemoBlock.vue'

const loading = ref(false)
const disabled = ref(false)

function toggleLoading() {
  loading.value = true
  setTimeout(() => (loading.value = false), 2000)
}
</script>

<template>
  <div class="max-w-3xl">
    <h1 class="text-2xl font-bold mb-2">Button 按钮</h1>
    <p class="text-muted-foreground mb-6">触发操作或事件时使用，支持 6 种变体、3 种尺寸、loading 和 disabled 状态。</p>

    <DemoBlock
      title="按钮变体"
      description="6 种视觉风格：default、destructive、outline、secondary、ghost、link"
      code='<EButton variant="default">默认</EButton>
<EButton variant="destructive">危险</EButton>
<EButton variant="outline">描边</EButton>
<EButton variant="secondary">次要</EButton>
<EButton variant="ghost">幽灵</EButton>
<EButton variant="link">链接</EButton>'
    >
      <div class="flex flex-wrap gap-3">
        <EButton variant="default">默认</EButton>
        <EButton variant="destructive">危险</EButton>
        <EButton variant="outline">描边</EButton>
        <EButton variant="secondary">次要</EButton>
        <EButton variant="ghost">幽灵</EButton>
        <EButton variant="link">链接</EButton>
      </div>
    </DemoBlock>

    <DemoBlock
      title="按钮尺寸"
      description="3 种标准尺寸：sm、default、lg，以及图标专用尺寸"
      code='<EButton size="sm">小号</EButton>
<EButton size="default">默认</EButton>
<EButton size="lg">大号</EButton>'
    >
      <div class="flex flex-wrap items-center gap-3">
        <EButton size="sm">小号</EButton>
        <EButton size="default">默认</EButton>
        <EButton size="lg">大号</EButton>
      </div>
    </DemoBlock>

    <DemoBlock
      title="Loading 状态"
      description="按钮处于加载中时自动显示 spinner 并禁用点击"
      code='<EButton :loading="loading" @click="toggleLoading">
  点击触发 2 秒 Loading
</EButton>'
    >
      <div class="flex flex-wrap gap-3">
        <EButton :loading="loading" @click="toggleLoading">
          {{ loading ? '加载中...' : '点击触发 2 秒 Loading' }}
        </EButton>
        <EButton variant="outline" :loading="loading">描边 Loading</EButton>
        <EButton variant="secondary" :loading="true">固定 Loading</EButton>
      </div>
    </DemoBlock>

    <DemoBlock
      title="Disabled 状态"
      description="禁用按钮后不响应任何交互"
      code='<EButton :disabled="true">禁用按钮</EButton>'
    >
      <div class="flex flex-wrap gap-3 items-center">
        <EButton :disabled="disabled">{{ disabled ? '已禁用' : '可点击' }}</EButton>
        <EButton variant="outline" :disabled="disabled">描边禁用</EButton>
        <EButton variant="secondary" :disabled="disabled">次要禁用</EButton>
        <EButton variant="outline" @click="disabled = !disabled">
          {{ disabled ? '解除禁用' : '设为禁用' }}
        </EButton>
      </div>
    </DemoBlock>

    <DemoBlock
      title="图标按钮"
      description="使用 icon / icon-sm / icon-lg 尺寸创建正方形图标按钮"
      code='<EButton size="icon" variant="outline"><X class="size-4" /></EButton>
<EButton size="icon-sm"><Plus class="size-4" /></EButton>
<EButton size="icon-lg" variant="destructive"><AlertTriangle class="size-4" /></EButton>'
    >
      <div class="flex flex-wrap gap-3 items-center">
        <EButton size="icon" variant="outline"><X class="size-4" /></EButton>
        <EButton size="icon-sm"><Plus class="size-4" /></EButton>
        <EButton size="icon-lg" variant="secondary"><Settings class="size-4" /></EButton>
        <EButton size="icon-lg" variant="destructive"><AlertTriangle class="size-4" /></EButton>
        <EButton size="icon" variant="ghost"><HelpCircle class="size-4" /></EButton>
      </div>
    </DemoBlock>

    <DemoBlock
      title="组合示例"
      description="在实际场景中常见的按钮组合"
    >
      <div class="space-y-4">
        <div class="flex gap-2">
          <EButton>保存</EButton>
          <EButton variant="outline">取消</EButton>
        </div>
        <div class="flex gap-2">
          <EButton variant="destructive">删除记录</EButton>
          <EButton variant="outline">查看详情</EButton>
          <EButton variant="ghost">更多操作</EButton>
        </div>
        <div class="flex gap-2">
          <EButton size="sm" variant="outline">编辑</EButton>
          <EButton size="sm" variant="destructive">删除</EButton>
        </div>
      </div>
    </DemoBlock>
  </div>
</template>
