<script setup lang="ts">
import DemoBlock from '../components/DemoBlock.vue'
import ComponentDoc from '../components/ComponentDoc.vue'
import PropsTable from '../components/PropsTable.vue'
import EventsTable from '../components/EventsTable.vue'
import SlotsTable from '../components/SlotsTable.vue'

const tocItems = [
  { id: 'usage', label: '使用场景' },
  { id: 'popover-basic', label: '基础用法' },
  { id: 'popover-sides', label: '多方向' },
  { id: 'props', label: 'Props' },
  { id: 'events', label: 'Events' },
  { id: 'slots', label: 'Slots' },
]

const propsData = [
  { name: 'side', type: "'top' | 'right' | 'bottom' | 'left'", default: "'bottom'", description: '弹出方向' },
  { name: 'sideOffset', type: 'number', default: '-', description: '与触发元素的间距（px）' },
  { name: 'align', type: "'start' | 'center' | 'end'", default: "'center'", description: '对齐方式' },
  { name: 'open', type: 'boolean', default: 'false', description: '是否显示（v-model，受控模式）' },
  { name: 'class', type: 'string', default: '-', description: '自定义 CSS 类名' },
]

const eventsData = [
  { name: 'update:open', params: '(value: boolean)', description: '显示状态变化时触发' },
]

const slotsData = [
  { name: 'trigger', description: '触发 Popover 的目标元素' },
  { name: 'default', description: 'Popover 内容区域' },
]
</script>

<template>
  <ComponentDoc
    title="Popover 气泡卡片"
    description="Popover 用于展示富内容的气泡卡片，如用户信息预览、操作确认面板等，通过点击触发。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">Popover 适用于需要展示富内容的气泡卡片，如用户信息预览、操作确认面板等，通过点击触发并支持自定义内容。</p>
    </section>

    <section id="popover-basic">
      <DemoBlock
        title="基础用法"
        description="点击触发，显示富内容气泡卡片"
        code='<EPopover>
  <template #trigger>
    <EButton>打开 Popover</EButton>
  </template>
  <div class="p-3">Popover 内容</div>
</EPopover>'
      >
        <EPopover>
          <template #trigger>
            <EButton variant="outline">点击打开 Popover</EButton>
          </template>
          <div class="p-3 min-w-[200px]">
            <h4 class="font-semibold mb-2">用户信息</h4>
            <div class="space-y-1 text-sm">
              <div class="flex justify-between">
                <span class="text-muted-foreground">姓名</span>
                <span>张三</span>
              </div>
              <div class="flex justify-between">
                <span class="text-muted-foreground">角色</span>
                <span>管理员</span>
              </div>
              <div class="flex justify-between">
                <span class="text-muted-foreground">状态</span>
                <EBadge variant="default">在线</EBadge>
              </div>
            </div>
            <div class="mt-3 pt-3 border-t flex gap-2">
              <EButton size="sm" class="flex-1">查看详情</EButton>
              <EButton size="sm" variant="outline">消息</EButton>
            </div>
          </div>
        </EPopover>
      </DemoBlock>
    </section>

    <section id="popover-sides">
      <DemoBlock
        title="多方向"
        description="通过 side 和 align 控制弹出位置"
      >
        <div class="flex flex-wrap gap-3">
          <EPopover side="top">
            <template #trigger>
              <EButton variant="outline" size="sm">顶部</EButton>
            </template>
            <div class="p-3 text-sm">顶部 Popover 内容</div>
          </EPopover>
          <EPopover side="bottom">
            <template #trigger>
              <EButton variant="outline" size="sm">底部</EButton>
            </template>
            <div class="p-3 text-sm">底部 Popover 内容</div>
          </EPopover>
          <EPopover side="left">
            <template #trigger>
              <EButton variant="outline" size="sm">左侧</EButton>
            </template>
            <div class="p-3 text-sm">左侧 Popover 内容</div>
          </EPopover>
          <EPopover side="right">
            <template #trigger>
              <EButton variant="outline" size="sm">右侧</EButton>
            </template>
            <div class="p-3 text-sm">右侧 Popover 内容</div>
          </EPopover>
        </div>
      </DemoBlock>
    </section>

    <section id="props">
      <h2 class="text-lg font-semibold mb-3">Popover Props</h2>
      <PropsTable :data="propsData" />
    </section>

    <section id="events">
      <h2 class="text-lg font-semibold mb-3">Popover Events</h2>
      <EventsTable :data="eventsData" />
    </section>

    <section id="slots">
      <h2 class="text-lg font-semibold mb-3">Popover Slots</h2>
      <SlotsTable :data="slotsData" />
    </section>
  </ComponentDoc>
</template>
