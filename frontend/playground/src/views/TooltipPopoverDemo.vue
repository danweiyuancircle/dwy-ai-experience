<script setup lang="ts">
import { ref } from 'vue'
import DemoBlock from '../components/DemoBlock.vue'
import ComponentDoc from '../components/ComponentDoc.vue'
import PropsTable from '../components/PropsTable.vue'
import EventsTable from '../components/EventsTable.vue'
import SlotsTable from '../components/SlotsTable.vue'

const popoverOpen = ref(false)

const tocItems = [
  { id: 'usage', label: '使用场景' },
  { id: 'tooltip-basic', label: 'Tooltip 基础用法' },
  { id: 'tooltip-delay', label: 'Tooltip 延迟' },
  { id: 'popover-basic', label: 'Popover 基础用法' },
  { id: 'popover-sides', label: 'Popover 多方向' },
  { id: 'tooltip-props', label: 'Tooltip Props' },
  { id: 'tooltip-slots', label: 'Tooltip Slots' },
  { id: 'popover-props', label: 'Popover Props' },
  { id: 'popover-events', label: 'Popover Events' },
  { id: 'popover-slots', label: 'Popover Slots' },
]

const tooltipPropsData = [
  { name: 'content', type: 'string', default: '-', description: '提示文字内容' },
  { name: 'side', type: "'top' | 'right' | 'bottom' | 'left'", default: "'top'", description: '弹出方向' },
  { name: 'sideOffset', type: 'number', default: '-', description: '与触发元素的间距（px）' },
  { name: 'delayDuration', type: 'number', default: '-', description: '悬停后延迟显示的时间（毫秒）' },
  { name: 'disabled', type: 'boolean', default: 'false', description: '是否禁用 Tooltip' },
  { name: 'class', type: 'string', default: '-', description: '自定义 CSS 类名' },
]

const tooltipSlotsData = [
  { name: 'default', description: '触发 Tooltip 的目标元素' },
]

const popoverPropsData = [
  { name: 'side', type: "'top' | 'right' | 'bottom' | 'left'", default: "'bottom'", description: '弹出方向' },
  { name: 'sideOffset', type: 'number', default: '-', description: '与触发元素的间距（px）' },
  { name: 'align', type: "'start' | 'center' | 'end'", default: "'center'", description: '对齐方式' },
  { name: 'open', type: 'boolean', default: 'false', description: '是否显示（v-model，受控模式）' },
  { name: 'class', type: 'string', default: '-', description: '自定义 CSS 类名' },
]

const popoverEventsData = [
  { name: 'update:open', params: '(value: boolean)', description: '显示状态变化时触发' },
]

const popoverSlotsData = [
  { name: 'trigger', description: '触发 Popover 的目标元素' },
  { name: 'default', description: 'Popover 内容区域' },
]
</script>

<template>
  <ComponentDoc
    title="Tooltip & Popover"
    description="Tooltip 用于简短文字提示，Popover 用于富内容气泡卡片。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">Tooltip 适用于鼠标悬停时展示简短文字说明，如图标按钮的功能提示、表格列标题的完整文本等。Popover 适用于需要展示富内容的气泡卡片，如用户信息预览、操作确认面板等，通过点击触发并支持自定义内容。</p>
    </section>

    <section id="tooltip-basic">
      <DemoBlock
        title="Tooltip 基础用法"
        description="悬停时显示简短提示文字"
        code='<ETooltip content="这是一条提示信息">
  <EButton>悬停查看提示</EButton>
</ETooltip>'
      >
        <div class="flex flex-wrap gap-3">
          <ETooltip content="这是顶部提示" side="top">
            <EButton variant="outline">顶部 Top</EButton>
          </ETooltip>
          <ETooltip content="这是底部提示" side="bottom">
            <EButton variant="outline">底部 Bottom</EButton>
          </ETooltip>
          <ETooltip content="这是左侧提示" side="left">
            <EButton variant="outline">左侧 Left</EButton>
          </ETooltip>
          <ETooltip content="这是右侧提示" side="right">
            <EButton variant="outline">右侧 Right</EButton>
          </ETooltip>
        </div>
      </DemoBlock>
    </section>

    <section id="tooltip-delay">
      <DemoBlock
        title="Tooltip 延迟"
        description="通过 delayDuration 控制显示延迟（毫秒）"
        code='<ETooltip content="延迟 500ms 显示" :delayDuration="500">
  <EButton>延迟 Tooltip</EButton>
</ETooltip>'
      >
        <div class="flex gap-3">
          <ETooltip content="即时显示（0ms）" :delayDuration="0">
            <EButton variant="outline" size="sm">即时</EButton>
          </ETooltip>
          <ETooltip content="延迟 300ms 显示" :delayDuration="300">
            <EButton variant="outline" size="sm">300ms 延迟</EButton>
          </ETooltip>
          <ETooltip content="延迟 800ms 显示" :delayDuration="800">
            <EButton variant="outline" size="sm">800ms 延迟</EButton>
          </ETooltip>
        </div>
      </DemoBlock>
    </section>

    <section id="popover-basic">
      <DemoBlock
        title="Popover 基础用法"
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
        title="Popover 多方向"
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

    <section id="tooltip-props">
      <h2 class="text-lg font-semibold mb-3">Tooltip Props</h2>
      <PropsTable :data="tooltipPropsData" />
    </section>

    <section id="tooltip-slots">
      <h2 class="text-lg font-semibold mb-3">Tooltip Slots</h2>
      <SlotsTable :data="tooltipSlotsData" />
    </section>

    <section id="popover-props">
      <h2 class="text-lg font-semibold mb-3">Popover Props</h2>
      <PropsTable :data="popoverPropsData" />
    </section>

    <section id="popover-events">
      <h2 class="text-lg font-semibold mb-3">Popover Events</h2>
      <EventsTable :data="popoverEventsData" />
    </section>

    <section id="popover-slots">
      <h2 class="text-lg font-semibold mb-3">Popover Slots</h2>
      <SlotsTable :data="popoverSlotsData" />
    </section>
  </ComponentDoc>
</template>
