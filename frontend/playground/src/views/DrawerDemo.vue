<script setup lang="ts">
import { ref } from 'vue'
import DemoBlock from '../components/DemoBlock.vue'
import ComponentDoc from '../components/ComponentDoc.vue'
import PropsTable from '../components/PropsTable.vue'
import EventsTable from '../components/EventsTable.vue'
import SlotsTable from '../components/SlotsTable.vue'

const drawerRight = ref(false)
const drawerLeft = ref(false)
const drawerTop = ref(false)
const drawerBottom = ref(false)

const tocItems = [
  { id: 'usage', label: '使用场景' },
  { id: 'drawer-right', label: '右侧抽屉' },
  { id: 'drawer-directions', label: '多方向抽屉' },
  { id: 'props', label: 'Props' },
  { id: 'events', label: 'Events' },
  { id: 'slots', label: 'Slots' },
]

const propsData = [
  { name: 'open', type: 'boolean', default: 'false', description: '是否显示抽屉（v-model）' },
  { name: 'title', type: 'string', default: '-', description: '抽屉标题' },
  { name: 'description', type: 'string', default: '-', description: '抽屉描述文字' },
  { name: 'direction', type: "'top' | 'right' | 'bottom' | 'left'", default: "'right'", description: '抽屉滑出方向' },
  { name: 'showClose', type: 'boolean', default: 'true', description: '是否显示关闭按钮' },
  { name: 'class', type: 'string', default: '-', description: '自定义 CSS 类名' },
]

const eventsData = [
  { name: 'update:open', params: '(value: boolean)', description: '抽屉显示状态变化时触发' },
  { name: 'close', params: '()', description: '抽屉关闭时触发' },
]

const slotsData = [
  { name: 'default', description: '抽屉主体内容' },
]
</script>

<template>
  <ComponentDoc
    title="Drawer 抽屉"
    description="抽屉组件，从屏幕边缘滑入的面板，适用于详情面板、筛选侧栏、设置面板等场景。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">Drawer 适用于详情面板、筛选侧栏、设置面板等从屏幕边缘滑入的场景，支持上下左右四个方向。</p>
    </section>

    <section id="drawer-right">
      <DemoBlock
        title="右侧抽屉"
        description="从右侧滑入的抽屉（默认方向）"
        code='<EDrawer v-model:open="open" title="用户详情" direction="right">
  内容区域
</EDrawer>'
      >
        <EButton @click="drawerRight = true">右侧抽屉</EButton>
        <EDrawer v-model:open="drawerRight" title="用户详情" direction="right">
          <div class="p-4 space-y-3">
            <p class="text-muted-foreground">这里是抽屉的内容区域，可以放置任何内容。</p>
            <EDescriptions :items="[
              { label: '姓名', value: '张三' },
              { label: '邮箱', value: 'zhangsan@example.com' },
              { label: '角色', value: '管理员' },
              { label: '状态', value: '在职' },
            ]" />
          </div>
        </EDrawer>
      </DemoBlock>
    </section>

    <section id="drawer-directions">
      <DemoBlock
        title="多方向抽屉"
        description="支持 top / right / bottom / left 四个方向"
      >
        <div class="flex flex-wrap gap-2">
          <EButton variant="outline" @click="drawerLeft = true">左侧</EButton>
          <EButton variant="outline" @click="drawerRight = true">右侧</EButton>
          <EButton variant="outline" @click="drawerTop = true">顶部</EButton>
          <EButton variant="outline" @click="drawerBottom = true">底部</EButton>
        </div>
        <EDrawer v-model:open="drawerLeft" title="左侧抽屉" direction="left">
          <div class="p-4"><p class="text-muted-foreground">左侧抽屉内容</p></div>
        </EDrawer>
        <EDrawer v-model:open="drawerTop" title="顶部抽屉" direction="top">
          <div class="p-4"><p class="text-muted-foreground">顶部抽屉内容</p></div>
        </EDrawer>
        <EDrawer v-model:open="drawerBottom" title="底部抽屉" direction="bottom">
          <div class="p-4"><p class="text-muted-foreground">底部抽屉内容</p></div>
        </EDrawer>
      </DemoBlock>
    </section>

    <section id="props">
      <h2 class="text-lg font-semibold mb-3">Drawer Props</h2>
      <PropsTable :data="propsData" />
    </section>

    <section id="events">
      <h2 class="text-lg font-semibold mb-3">Drawer Events</h2>
      <EventsTable :data="eventsData" />
    </section>

    <section id="slots">
      <h2 class="text-lg font-semibold mb-3">Drawer Slots</h2>
      <SlotsTable :data="slotsData" />
    </section>
  </ComponentDoc>
</template>
