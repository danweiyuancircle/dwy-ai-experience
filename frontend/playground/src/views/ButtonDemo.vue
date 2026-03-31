<script setup lang="ts">
import { ref } from 'vue'
import { X, Plus, Settings, AlertTriangle, HelpCircle } from 'lucide-vue-next'
import DemoBlock from '../components/DemoBlock.vue'
import ComponentDoc from '../components/ComponentDoc.vue'
import PropsTable from '../components/PropsTable.vue'
import EventsTable from '../components/EventsTable.vue'
import SlotsTable from '../components/SlotsTable.vue'

const loading = ref(false)
const disabled = ref(false)

function toggleLoading() {
  loading.value = true
  setTimeout(() => (loading.value = false), 2000)
}

const tocItems = [
  { id: 'usage', label: '使用场景' },
  { id: 'variants', label: '变体样式' },
  { id: 'sizes', label: '按钮尺寸' },
  { id: 'loading', label: '加载状态' },
  { id: 'disabled', label: '禁用状态' },
  { id: 'icon', label: '图标按钮' },
  { id: 'combo', label: '组合示例' },
  { id: 'props', label: 'Props' },
  { id: 'events', label: 'Events' },
  { id: 'slots', label: 'Slots' },
]

const propsData = [
  { name: 'variant', type: "'default' | 'destructive' | 'outline' | 'secondary' | 'ghost' | 'link'", default: "'default'", description: '按钮变体样式' },
  { name: 'size', type: "'default' | 'sm' | 'lg' | 'icon' | 'icon-sm' | 'icon-lg'", default: "'default'", description: '按钮尺寸' },
  { name: 'loading', type: 'boolean', default: 'false', description: '加载状态，禁用点击并显示 spinner' },
  { name: 'disabled', type: 'boolean', default: 'false', description: '是否禁用' },
  { name: 'as', type: 'string | Component', default: "'button'", description: '渲染的 HTML 标签或组件' },
  { name: 'class', type: 'string', description: '自定义 CSS 类名，通过 cn() 合并' },
]

const eventsData = [
  { name: 'click', params: '(event: MouseEvent)', description: '点击按钮时触发（原生事件）' },
]

const slotsData = [
  { name: 'default', description: '按钮内容（文字、图标等）' },
]
</script>

<template>
  <ComponentDoc
    title="Button 按钮"
    description="触发操作或事件时使用，支持 6 种变体、多种尺寸、loading 和 disabled 状态。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">适用于表单提交、对话框确认/取消、页面导航跳转、危险操作二次确认等交互场景。根据操作的重要性和语义选择不同的变体：主操作用 default，危险操作用 destructive，辅助操作用 outline/secondary，低优先级用 ghost/link。</p>
    </section>

    <section id="variants">
      <DemoBlock
        title="变体样式"
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
    </section>

    <section id="sizes">
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
    </section>

    <section id="loading">
      <DemoBlock
        title="加载状态"
        description="按钮处于加载中时自动显示 spinner 并禁用点击"
        code='<EButton :loading="loading" @click="toggleLoading">点击触发</EButton>'
      >
        <div class="flex flex-wrap gap-3">
          <EButton :loading="loading" @click="toggleLoading">
            {{ loading ? '加载中...' : '点击触发 2 秒 Loading' }}
          </EButton>
          <EButton variant="outline" :loading="loading">描边 Loading</EButton>
          <EButton variant="secondary" :loading="true">固定 Loading</EButton>
        </div>
      </DemoBlock>
    </section>

    <section id="disabled">
      <DemoBlock
        title="禁用状态"
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
    </section>

    <section id="icon">
      <DemoBlock
        title="图标按钮"
        description="使用 icon / icon-sm / icon-lg 尺寸创建正方形图标按钮"
        code='<EButton size="icon" variant="outline"><X /></EButton>'
      >
        <div class="flex flex-wrap gap-3 items-center">
          <EButton size="icon" variant="outline"><X class="size-4" /></EButton>
          <EButton size="icon-sm"><Plus class="size-4" /></EButton>
          <EButton size="icon-lg" variant="secondary"><Settings class="size-4" /></EButton>
          <EButton size="icon-lg" variant="destructive"><AlertTriangle class="size-4" /></EButton>
          <EButton size="icon" variant="ghost"><HelpCircle class="size-4" /></EButton>
        </div>
      </DemoBlock>
    </section>

    <section id="combo">
      <DemoBlock title="组合示例" description="在实际场景中常见的按钮组合">
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
        </div>
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
