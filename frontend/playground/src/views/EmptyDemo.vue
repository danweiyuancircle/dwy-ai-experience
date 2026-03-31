<script setup lang="ts">
import DemoBlock from '../components/DemoBlock.vue'
import ComponentDoc from '../components/ComponentDoc.vue'
import PropsTable from '../components/PropsTable.vue'
import SlotsTable from '../components/SlotsTable.vue'

const tocItems = [
  { id: 'usage', label: '使用场景' },
  { id: 'basic', label: '基础用法' },
  { id: 'props', label: 'Props' },
  { id: 'slots', label: 'Slots' },
]

const propsData = [
  { name: 'title', type: 'string', description: '空状态标题' },
  { name: 'description', type: 'string', description: '空状态描述文字' },
  { name: 'icon', type: 'string', description: '图标文本（也可通过 icon 插槽自定义）' },
  { name: 'class', type: 'string', description: '自定义 CSS 类名，通过 cn() 合并' },
]

const slotsData = [
  { name: 'default', description: '底部操作区域（如按钮）' },
  { name: 'icon', description: '自定义图标内容' },
  { name: 'title', description: '自定义标题内容' },
  { name: 'description', description: '自定义描述内容' },
]
</script>

<template>
  <ComponentDoc
    title="Empty 空状态"
    description="数据为空时的占位展示，支持自定义标题、描述、图标和操作按钮。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">适用于列表无数据、搜索无结果、初始化引导等场景。通过 title 和 description 传递提示信息，default 插槽可放置操作按钮引导用户添加数据。支持 icon、title、description 三个具名插槽用于完全自定义内容。</p>
    </section>

    <section id="basic">
      <DemoBlock
        title="基础用法"
        description="数据为空时的占位展示"
        code='<EEmpty title="暂无数据" description="添加一些数据后这里会显示内容" />'
      >
        <div class="space-y-6">
          <EEmpty />
          <ESeparator />
          <EEmpty title="暂无数据" description="点击上方按钮添加第一条记录" />
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
