<script setup lang="ts">
import { ref } from 'vue'
import DemoBlock from '../components/DemoBlock.vue'
import ComponentDoc from '../components/ComponentDoc.vue'
import PropsTable from '../components/PropsTable.vue'
import EventsTable from '../components/EventsTable.vue'
import SlotsTable from '../components/SlotsTable.vue'

const activeKey = ref('dashboard')
const collapsed = ref(false)

const menuItems = [
  {
    key: 'dashboard',
    label: '仪表盘',
  },
  {
    key: 'users',
    label: '用户管理',
    children: [
      { key: 'user-list', label: '用户列表' },
      { key: 'user-roles', label: '角色管理' },
    ],
  },
  {
    key: 'content',
    label: '内容管理',
    children: [
      { key: 'articles', label: '文章列表' },
      { key: 'categories', label: '分类管理' },
      { key: 'tags', label: '标签管理' },
    ],
  },
  {
    key: 'settings',
    label: '系统设置',
  },
  {
    key: 'profile',
    label: '个人中心',
    disabled: true,
  },
]

const tocItems = [
  { id: 'usage', label: '使用场景' },
  { id: 'basic', label: '基础菜单' },
  { id: 'accordion', label: '手风琴菜单' },
  { id: 'props', label: 'Props' },
  { id: 'events', label: 'Events' },
  { id: 'slots', label: 'Slots' },
]

const propsData = [
  { name: 'modelValue', type: 'string', default: '-', description: '当前激活菜单项的 key，支持 v-model' },
  { name: 'items', type: 'MenuItem[]', default: '[]', description: '菜单项数组，支持嵌套 children 子菜单' },
  { name: 'collapsed', type: 'boolean', default: 'false', description: '是否折叠菜单（仅显示图标）' },
  { name: 'router', type: 'boolean', default: 'false', description: '是否启用路由模式，点击菜单项使用 vue-router 导航' },
  { name: 'uniqueOpened', type: 'boolean', default: 'false', description: '是否同级只保持一个子菜单展开' },
  { name: 'defaultOpeneds', type: 'string[]', default: '[]', description: '初始展开的子菜单 key 列表' },
  { name: 'class', type: 'string', default: '-', description: '自定义 CSS 类名' },
]

const eventsData = [
  { name: 'update:modelValue', params: '(value: string)', description: '激活菜单项变更时触发' },
  { name: 'select', params: '(key: string)', description: '选中菜单项时触发' },
]

const slotsData = [
  { name: '-', description: 'EMenu 不提供自定义插槽，内容由 items 数据驱动渲染' },
]
</script>

<template>
  <ComponentDoc
    title="Menu 菜单"
    description="侧边导航菜单组件，支持子菜单、禁用项和折叠状态。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">适用于后台管理系统的侧边导航栏，支持多级嵌套子菜单、折叠收起、手风琴模式（同级互斥展开）和路由跳转。通过 items 数据驱动渲染菜单结构。</p>
    </section>

    <section id="basic">
      <DemoBlock
        title="基础菜单"
        description="使用 items 数组定义菜单项，支持嵌套子菜单"
        code='<EMenu v-model="activeKey" :items="menuItems" />'
      >
        <div class="flex gap-4">
          <div class="border rounded-lg overflow-hidden" :style="{ width: collapsed ? '64px' : '220px' }">
            <EMenu v-model="activeKey" :items="menuItems" :collapsed="collapsed" />
          </div>
          <div class="flex-1 space-y-3">
            <div class="p-4 bg-muted/30 rounded-md">
              <p class="text-sm text-muted-foreground">当前激活：<strong>{{ activeKey }}</strong></p>
            </div>
            <ESwitch v-model="collapsed" label="折叠菜单" />
          </div>
        </div>
      </DemoBlock>
    </section>

    <section id="accordion">
      <DemoBlock
        title="手风琴菜单"
        description="设置 unique-opened 保持同级只展开一个子菜单"
        code='<EMenu v-model="activeKey" :items="menuItems" unique-opened :default-openeds="[&apos;users&apos;]" />'
      >
        <div class="border rounded-lg overflow-hidden" style="width: 220px">
          <EMenu v-model="activeKey" :items="menuItems" unique-opened :default-openeds="['users']" />
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
