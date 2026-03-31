<script setup lang="ts">
import DemoBlock from '../components/DemoBlock.vue'
import ComponentDoc from '../components/ComponentDoc.vue'
import PropsTable from '../components/PropsTable.vue'
import SlotsTable from '../components/SlotsTable.vue'

const tags = Array.from({ length: 50 }, (_, i) => `v1.${i}.0`)

const tocItems = [
  { id: 'usage', label: '使用场景' },
  { id: 'basic', label: '基础滚动' },
  { id: 'props', label: 'Props' },
  { id: 'slots', label: 'Slots' },
]

const propsData = [
  { name: 'type', type: "'auto' | 'always' | 'scroll' | 'hover'", default: "'hover'", description: "滚动条显示策略：auto 自动、always 始终显示、scroll 滚动时显示、hover 悬停时显示" },
  { name: 'class', type: 'string', description: '自定义 CSS 类名' },
]

const slotsData = [
  { name: 'default', description: '可滚动的内容区域' },
]
</script>

<template>
  <ComponentDoc
    title="ScrollArea 滚动区域"
    description="自定义样式的滚动容器，替代浏览器原生滚动条，提供统一的跨浏览器滚动体验。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">适用于需要自定义滚动条样式的区域，如侧边栏导航、下拉菜单长列表、代码编辑器内容区域等。通过 type 属性控制滚动条的显示时机，保持界面整洁。</p>
    </section>

    <section id="basic">
      <DemoBlock
        title="基础滚动"
        description="固定高度容器内的长列表，鼠标悬停时显示自定义滚动条"
        code='<EScrollArea class="h-72 w-48 rounded-md border">
  <div class="p-4">
    <h4 class="mb-4 text-sm font-medium">版本列表</h4>
    <div v-for="tag in tags" :key="tag">
      {{ tag }}
    </div>
  </div>
</EScrollArea>'
      >
        <EScrollArea class="h-72 w-48 rounded-md border">
          <div class="p-4">
            <h4 class="mb-4 text-sm font-medium leading-none">版本列表</h4>
            <div v-for="tag in tags" :key="tag" class="text-sm py-1.5">
              {{ tag }}
              <ESeparator class="my-1.5" />
            </div>
          </div>
        </EScrollArea>
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
