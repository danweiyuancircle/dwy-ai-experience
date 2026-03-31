<script setup lang="ts">
import DemoBlock from '../components/DemoBlock.vue'
import ComponentDoc from '../components/ComponentDoc.vue'
import PropsTable from '../components/PropsTable.vue'
import EventsTable from '../components/EventsTable.vue'
import SlotsTable from '../components/SlotsTable.vue'

const tocItems = [
  { id: 'usage', label: '使用场景' },
  { id: 'horizontal', label: '水平面板' },
  { id: 'vertical', label: '垂直面板' },
  { id: 'nested', label: '嵌套面板' },
  { id: 'with-handle', label: '拖拽手柄' },
  { id: 'group-props', label: 'PanelGroup Props' },
  { id: 'panel-props', label: 'Panel Props' },
  { id: 'handle-props', label: 'Handle Props' },
  { id: 'events', label: 'Events' },
  { id: 'slots', label: 'Slots' },
]

const groupPropsData = [
  { name: 'direction', type: "'horizontal' | 'vertical'", default: "'horizontal'", description: '面板排列方向' },
  { name: 'id', type: 'string', description: '持久化布局的唯一标识' },
  { name: 'class', type: 'string', description: '自定义 CSS 类名' },
]

const panelPropsData = [
  { name: 'defaultSize', type: 'number', description: '面板初始大小（百分比 0-100）' },
  { name: 'minSize', type: 'number', description: '面板最小大小（百分比）' },
  { name: 'maxSize', type: 'number', description: '面板最大大小（百分比）' },
  { name: 'id', type: 'string', description: '面板唯一标识' },
]

const handlePropsData = [
  { name: 'withHandle', type: 'boolean', default: 'false', description: '是否显示拖拽手柄图标' },
  { name: 'id', type: 'string', description: '手柄唯一标识' },
  { name: 'class', type: 'string', description: '自定义 CSS 类名' },
]

const eventsData = [
  { name: 'layout', params: '(sizes: number[])', description: '面板尺寸变化时触发（PanelGroup）' },
]

const slotsData = [
  { name: 'default (PanelGroup)', description: '放置 Panel 和 Handle 子组件' },
  { name: 'default (Panel)', description: '面板内容' },
]
</script>

<template>
  <ComponentDoc
    title="Resizable 可调整面板"
    description="可拖拽调整大小的面板组，支持水平/垂直方向和嵌套布局，常用于 IDE 布局、面板分割等场景。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">适用于需要用户自定义布局比例的场景，如代码编辑器的文件树/编辑区/终端分割、邮件客户端的列表/详情分栏、仪表盘面板调整等。</p>
    </section>

    <section id="horizontal">
      <DemoBlock
        title="水平面板"
        description="默认水平方向，拖拽分隔条调整左右面板宽度"
        code='<EResizablePanelGroup direction="horizontal">
  <EResizablePanel :default-size="50">左侧面板</EResizablePanel>
  <EResizableHandle />
  <EResizablePanel :default-size="50">右侧面板</EResizablePanel>
</EResizablePanelGroup>'
      >
        <div class="h-48 rounded-lg border">
          <EResizablePanelGroup direction="horizontal">
            <EResizablePanel :default-size="50">
              <div class="flex h-full items-center justify-center p-4">
                <span class="text-sm text-muted-foreground">左侧面板</span>
              </div>
            </EResizablePanel>
            <EResizableHandle />
            <EResizablePanel :default-size="50">
              <div class="flex h-full items-center justify-center p-4">
                <span class="text-sm text-muted-foreground">右侧面板</span>
              </div>
            </EResizablePanel>
          </EResizablePanelGroup>
        </div>
      </DemoBlock>
    </section>

    <section id="vertical">
      <DemoBlock
        title="垂直面板"
        description="direction='vertical' 时上下排列"
        code='<EResizablePanelGroup direction="vertical">
  <EResizablePanel :default-size="40">顶部面板</EResizablePanel>
  <EResizableHandle />
  <EResizablePanel :default-size="60">底部面板</EResizablePanel>
</EResizablePanelGroup>'
      >
        <div class="h-64 rounded-lg border">
          <EResizablePanelGroup direction="vertical">
            <EResizablePanel :default-size="40">
              <div class="flex h-full items-center justify-center p-4">
                <span class="text-sm text-muted-foreground">顶部面板</span>
              </div>
            </EResizablePanel>
            <EResizableHandle />
            <EResizablePanel :default-size="60">
              <div class="flex h-full items-center justify-center p-4">
                <span class="text-sm text-muted-foreground">底部面板</span>
              </div>
            </EResizablePanel>
          </EResizablePanelGroup>
        </div>
      </DemoBlock>
    </section>

    <section id="nested">
      <DemoBlock
        title="嵌套面板"
        description="面板内可以嵌套另一个 PanelGroup，实现复杂布局"
      >
        <div class="h-72 rounded-lg border">
          <EResizablePanelGroup direction="horizontal">
            <EResizablePanel :default-size="30" :min-size="20">
              <div class="flex h-full items-center justify-center p-4">
                <span class="text-sm text-muted-foreground">侧边栏</span>
              </div>
            </EResizablePanel>
            <EResizableHandle with-handle />
            <EResizablePanel :default-size="70">
              <EResizablePanelGroup direction="vertical">
                <EResizablePanel :default-size="60">
                  <div class="flex h-full items-center justify-center p-4">
                    <span class="text-sm text-muted-foreground">主内容区</span>
                  </div>
                </EResizablePanel>
                <EResizableHandle with-handle />
                <EResizablePanel :default-size="40" :min-size="20">
                  <div class="flex h-full items-center justify-center p-4">
                    <span class="text-sm text-muted-foreground">终端 / 输出</span>
                  </div>
                </EResizablePanel>
              </EResizablePanelGroup>
            </EResizablePanel>
          </EResizablePanelGroup>
        </div>
      </DemoBlock>
    </section>

    <section id="with-handle">
      <DemoBlock
        title="拖拽手柄"
        description="withHandle 属性显示可视化拖拽手柄，提升交互可见性"
        code='<EResizablePanelGroup direction="horizontal">
  <EResizablePanel :default-size="30">A</EResizablePanel>
  <EResizableHandle with-handle />
  <EResizablePanel :default-size="40">B</EResizablePanel>
  <EResizableHandle with-handle />
  <EResizablePanel :default-size="30">C</EResizablePanel>
</EResizablePanelGroup>'
      >
        <div class="h-40 rounded-lg border">
          <EResizablePanelGroup direction="horizontal">
            <EResizablePanel :default-size="30">
              <div class="flex h-full items-center justify-center p-4">
                <span class="text-sm font-medium">面板 A</span>
              </div>
            </EResizablePanel>
            <EResizableHandle with-handle />
            <EResizablePanel :default-size="40">
              <div class="flex h-full items-center justify-center p-4">
                <span class="text-sm font-medium">面板 B</span>
              </div>
            </EResizablePanel>
            <EResizableHandle with-handle />
            <EResizablePanel :default-size="30">
              <div class="flex h-full items-center justify-center p-4">
                <span class="text-sm font-medium">面板 C</span>
              </div>
            </EResizablePanel>
          </EResizablePanelGroup>
        </div>
      </DemoBlock>
    </section>

    <section id="group-props">
      <h2 class="text-lg font-semibold mb-3">EResizablePanelGroup Props</h2>
      <PropsTable :data="groupPropsData" />
    </section>

    <section id="panel-props">
      <h2 class="text-lg font-semibold mb-3">EResizablePanel Props</h2>
      <PropsTable :data="panelPropsData" />
    </section>

    <section id="handle-props">
      <h2 class="text-lg font-semibold mb-3">EResizableHandle Props</h2>
      <PropsTable :data="handlePropsData" />
    </section>

    <section id="events">
      <EventsTable :data="eventsData" />
    </section>

    <section id="slots">
      <SlotsTable :data="slotsData" />
    </section>
  </ComponentDoc>
</template>
