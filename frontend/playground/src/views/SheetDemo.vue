<script setup lang="ts">
import { ref } from 'vue'
import DemoBlock from '../components/DemoBlock.vue'
import ComponentDoc from '../components/ComponentDoc.vue'
import PropsTable from '../components/PropsTable.vue'
import EventsTable from '../components/EventsTable.vue'
import SlotsTable from '../components/SlotsTable.vue'

const rightOpen = ref(false)
const leftOpen = ref(false)
const topOpen = ref(false)
const bottomOpen = ref(false)

const tocItems = [
  { id: 'usage', label: '使用场景' },
  { id: 'directions', label: '四个方向' },
  { id: 'props', label: 'Props' },
  { id: 'events', label: 'Events' },
  { id: 'slots', label: 'Slots' },
]

const propsData = [
  { name: 'open', type: 'boolean', default: 'false', description: '控制面板的显示/隐藏' },
  { name: 'title', type: 'string', description: '面板标题' },
  { name: 'description', type: 'string', description: '面板描述内容' },
  { name: 'side', type: "'top' | 'right' | 'bottom' | 'left'", default: "'right'", description: '面板滑出方向' },
  { name: 'showClose', type: 'boolean', default: 'true', description: '是否显示关闭按钮' },
  { name: 'class', type: 'string', description: '自定义 CSS 类名' },
]

const eventsData = [
  { name: 'update:open', params: '(value: boolean)', description: '面板打开/关闭时触发' },
  { name: 'close', params: '()', description: '面板关闭时触发' },
]

const slotsData = [
  { name: 'trigger', description: '触发器内容，点击后打开面板' },
  { name: 'header', description: '自定义头部区域' },
  { name: 'default', description: '面板主体内容' },
  { name: 'footer', description: '自定义底部区域' },
]
</script>

<template>
  <ComponentDoc
    title="Sheet 侧边面板"
    description="从屏幕边缘滑出的面板，支持上/右/下/左四个方向，适用于表单编辑、详情查看等不离开当前页面的操作。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">适用于需要在当前页面上下文中编辑内容的场景，如筛选面板、详情查看、移动端导航菜单等。相比 Dialog 占据更大的屏幕面积，适合展示更多内容。</p>
    </section>

    <section id="directions">
      <DemoBlock
        title="四个方向"
        description="通过 side 属性设置面板从不同方向滑出"
        code='<ESheet v-model:open="rightOpen" side="right" title="右侧面板">
  <p>从右侧滑出的面板内容</p>
</ESheet>'
      >
        <div class="flex flex-wrap gap-3">
          <EButton variant="outline" @click="topOpen = true">上方滑出</EButton>
          <EButton variant="outline" @click="rightOpen = true">右侧滑出</EButton>
          <EButton variant="outline" @click="bottomOpen = true">下方滑出</EButton>
          <EButton variant="outline" @click="leftOpen = true">左侧滑出</EButton>
        </div>

        <ESheet v-model:open="topOpen" side="top" title="上方面板" description="从屏幕顶部滑出">
          <p class="text-sm text-muted-foreground">这是从上方滑出的面板内容。适合用于通知栏、搜索面板等场景。</p>
        </ESheet>

        <ESheet v-model:open="rightOpen" side="right" title="右侧面板" description="从屏幕右侧滑出">
          <p class="text-sm text-muted-foreground">这是从右侧滑出的面板内容。适合用于详情查看、表单编辑等场景。</p>
        </ESheet>

        <ESheet v-model:open="bottomOpen" side="bottom" title="下方面板" description="从屏幕底部滑出">
          <p class="text-sm text-muted-foreground">这是从下方滑出的面板内容。适合用于移动端操作菜单等场景。</p>
        </ESheet>

        <ESheet v-model:open="leftOpen" side="left" title="左侧面板" description="从屏幕左侧滑出">
          <p class="text-sm text-muted-foreground">这是从左侧滑出的面板内容。适合用于导航菜单等场景。</p>
        </ESheet>
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
