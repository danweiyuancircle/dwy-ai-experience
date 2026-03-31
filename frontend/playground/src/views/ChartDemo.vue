<script setup lang="ts">
import DemoBlock from '../components/DemoBlock.vue'
import ComponentDoc from '../components/ComponentDoc.vue'
import PropsTable from '../components/PropsTable.vue'
import SlotsTable from '../components/SlotsTable.vue'

const basicConfig = {
  revenue: { label: '收入', color: '#3b82f6' },
  expenses: { label: '支出', color: '#ef4444' },
}

const multiConfig = {
  frontend: { label: '前端', color: '#3b82f6' },
  backend: { label: '后端', color: '#10b981' },
  design: { label: '设计', color: '#8b5cf6' },
  product: { label: '产品', color: '#f59e0b' },
  devops: { label: '运维', color: '#ef4444' },
}

const tocItems = [
  { id: 'usage', label: '使用场景' },
  { id: 'basic', label: '基础用法' },
  { id: 'multi', label: '多数据系列' },
  { id: 'props', label: 'Props' },
  { id: 'slots', label: 'Slots' },
]

const propsData = [
  { name: 'config', type: 'ChartConfig', description: '图表配置，定义每个数据系列的 label 和 color，会生成对应的 CSS 变量（--color-{key}）' },
  { name: 'id', type: 'string', description: '图表唯一标识，未传入时自动生成随机 ID' },
  { name: 'class', type: 'string', description: '自定义 CSS 类名' },
]

const slotsData = [
  { name: 'default', props: '{ id: string, config: ChartConfig }', description: '图表内容区域，接收 id 和 config 作为插槽参数' },
]
</script>

<template>
  <ComponentDoc
    title="Chart 图表容器"
    description="图表基础容器组件，通过 ChartConfig 管理数据系列的颜色和标签，提供 CSS 变量注入和 provide/inject 能力，可搭配任意图表库使用。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">ChartContainer 是图表的基础包装器，不直接渲染图表。它通过 config 定义数据系列（系列名、颜色、标签），将颜色注入为 CSS 变量（如 --color-revenue），并通过 provide 将配置传递给子组件。开发者可在默认插槽中使用 ECharts、Chart.js 等任意图表库渲染实际图表。</p>
    </section>

    <section id="basic">
      <DemoBlock
        title="基础用法"
        description="定义收入/支出两个数据系列，容器自动注入对应的 CSS 颜色变量"
        code='<EChartContainer :config="basicConfig" id="demo-chart">
  <template #default="{ config }">
    <div class="flex items-center gap-6">
      <div v-for="(value, key) in config" :key="key" class="flex items-center gap-2">
        <div class="size-3 rounded-full" :style="{ backgroundColor: value.color }" />
        <span>{{ value.label }}</span>
      </div>
    </div>
    <!-- 这里放置实际图表（ECharts / Chart.js 等） -->
    <div class="mt-4 flex-1 rounded-lg border-2 border-dashed flex items-center justify-center text-muted-foreground">
      图表渲染区域
    </div>
  </template>
</EChartContainer>'
      >
        <div class="h-[300px]">
          <EChartContainer :config="basicConfig" id="demo-basic">
            <template #default="{ config }">
              <div class="flex items-center gap-6 mb-4">
                <div v-for="(value, key) in config" :key="key" class="flex items-center gap-2">
                  <div class="size-3 rounded-full" :style="{ backgroundColor: value.color }" />
                  <span class="text-sm">{{ value.label }}</span>
                </div>
              </div>
              <div class="flex-1 rounded-lg border-2 border-dashed flex items-center justify-center text-muted-foreground">
                <div class="text-center">
                  <p class="text-lg font-medium mb-1">图表渲染区域</p>
                  <p class="text-xs">在此处使用 ECharts / Chart.js 等库渲染图表</p>
                  <p class="text-xs mt-1">可通过 var(--color-revenue)、var(--color-expenses) 获取颜色</p>
                </div>
              </div>
            </template>
          </EChartContainer>
        </div>
      </DemoBlock>
    </section>

    <section id="multi">
      <DemoBlock
        title="多数据系列"
        description="支持任意数量的数据系列，每个系列都会生成独立的 CSS 颜色变量"
        code='<EChartContainer :config="multiConfig" id="multi-chart">
  ...
</EChartContainer>'
      >
        <div class="h-[300px]">
          <EChartContainer :config="multiConfig" id="demo-multi">
            <template #default="{ config }">
              <div class="flex flex-wrap items-center gap-4 mb-4">
                <div v-for="(value, key) in config" :key="key" class="flex items-center gap-2">
                  <div class="size-3 rounded-full" :style="{ backgroundColor: value.color }" />
                  <span class="text-sm">{{ value.label }}</span>
                </div>
              </div>
              <div class="flex-1 flex gap-3 items-end px-4">
                <div
                  v-for="(value, key) in config"
                  :key="key"
                  class="flex-1 rounded-t-md flex items-end justify-center pb-2 text-white text-xs font-medium"
                  :style="{
                    backgroundColor: value.color,
                    height: `${Math.floor(Math.random() * 60 + 40)}%`,
                  }"
                >
                  {{ value.label }}
                </div>
              </div>
            </template>
          </EChartContainer>
        </div>
      </DemoBlock>
    </section>

    <section id="props">
      <PropsTable :data="propsData" />
    </section>

    <section id="slots">
      <SlotsTable :data="slotsData" />
    </section>
  </ComponentDoc>
</template>
