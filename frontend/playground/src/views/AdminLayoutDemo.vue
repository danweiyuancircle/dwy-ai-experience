<script setup lang="ts">
import { ref } from 'vue'
import DemoBlock from '../components/DemoBlock.vue'
import ComponentDoc from '../components/ComponentDoc.vue'
import PropsTable from '../components/PropsTable.vue'
import EventsTable from '../components/EventsTable.vue'
import SlotsTable from '../components/SlotsTable.vue'

const activeKey = ref('dashboard')
const isCollapsed = ref(false)

const menuItems = [
  {
    key: 'dashboard',
    label: '工作台',
    icon: 'LayoutDashboard',
  },
  {
    key: 'users',
    label: '用户管理',
    icon: 'Users',
    children: [
      { key: 'user-list', label: '用户列表' },
      { key: 'user-roles', label: '角色管理' },
      { key: 'user-permissions', label: '权限设置' },
    ],
  },
  {
    key: 'content',
    label: '内容管理',
    icon: 'FileText',
    children: [
      { key: 'articles', label: '文章管理' },
      { key: 'categories', label: '分类管理' },
    ],
  },
  {
    key: 'system',
    label: '系统设置',
    icon: 'Settings',
    children: [
      { key: 'basic', label: '基础设置' },
      { key: 'security', label: '安全设置' },
      { key: 'logs', label: '操作日志' },
    ],
  },
]

function handleMenuSelect(key: string) {
  activeKey.value = key
}

const tocItems = [
  { id: 'usage', label: '使用场景' },
  { id: 'basic', label: '基础布局' },
  { id: 'collapsed', label: '折叠侧边栏' },
  { id: 'props', label: 'Props' },
  { id: 'events', label: 'Events' },
  { id: 'slots', label: 'Slots' },
]

const propsData = [
  { name: 'logo', type: 'string', description: 'Logo 图片地址' },
  { name: 'title', type: 'string', description: '系统标题，折叠时自动隐藏' },
  { name: 'menuItems', type: 'MenuItem[]', default: '[]', description: '侧边栏菜单数据，支持多级嵌套' },
  { name: 'activeKey', type: 'string', description: '当前激活的菜单项 key，支持 v-model' },
  { name: 'collapsed', type: 'boolean', default: 'false', description: '侧边栏是否折叠，支持 v-model' },
  { name: 'showFooter', type: 'boolean', default: 'false', description: '是否显示底部区域' },
  { name: 'headerHeight', type: 'string | number', default: '56', description: '顶栏高度（px 或 CSS 值）' },
  { name: 'sidebarWidth', type: 'string | number', default: '240', description: '侧边栏展开宽度（px 或 CSS 值）' },
  { name: 'collapsedWidth', type: 'string | number', default: '56', description: '侧边栏折叠宽度（px 或 CSS 值）' },
]

const eventsData = [
  { name: 'update:activeKey', params: '(key: string)', description: '菜单激活项变化时触发' },
  { name: 'update:collapsed', params: '(value: boolean)', description: '侧边栏折叠状态变化时触发' },
  { name: 'menu-select', params: '(key: string)', description: '点击菜单项时触发' },
]

const slotsData = [
  { name: 'default', description: '主内容区域' },
  { name: 'logo', description: '自定义 Logo 区域' },
  { name: 'sidebar', description: '自定义侧边栏导航内容（替代内置 EMenu）' },
  { name: 'sidebar-footer', description: '侧边栏底部区域' },
  { name: 'header', description: '顶栏右侧内容（折叠按钮右侧）' },
  { name: 'footer', description: '底部 Footer 内容' },
]
</script>

<template>
  <ComponentDoc
    title="AdminLayout 管理后台布局"
    description="开箱即用的后台管理系统布局组件，包含侧边栏导航、顶栏和内容区域，支持菜单折叠和响应式适配。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">用于搭建后台管理系统的整体页面布局。提供侧边栏菜单导航、顶栏工具栏、主内容区域三部分结构，通过 menuItems 驱动侧边栏菜单，支持多级嵌套和折叠展开。</p>
    </section>

    <section id="basic">
      <DemoBlock
        title="基础布局"
        description="完整的后台布局，包含 Logo、侧边栏菜单和内容区域"
        code='<EAdminLayout
  v-model:active-key="activeKey"
  v-model:collapsed="isCollapsed"
  title="管理系统"
  :menu-items="menuItems"
  show-footer
>
  <template #header>
    <div class="ml-auto">欢迎回来，管理员</div>
  </template>
  <div>当前页面：{{ activeKey }}</div>
  <template #footer>
    &copy; 2026 管理系统
  </template>
</EAdminLayout>'
      >
        <div class="h-[500px] rounded-lg border overflow-hidden">
          <EAdminLayout
            v-model:active-key="activeKey"
            v-model:collapsed="isCollapsed"
            title="管理系统"
            :menu-items="menuItems"
            show-footer
          >
            <template #header>
              <div class="ml-auto text-sm text-muted-foreground">欢迎回来，管理员</div>
            </template>
            <div class="space-y-4">
              <h2 class="text-lg font-semibold">{{ activeKey }}</h2>
              <p class="text-muted-foreground text-sm">当前选中菜单：{{ activeKey }}。点击左侧菜单切换页面，点击汉堡按钮折叠侧边栏。</p>
              <div class="grid grid-cols-3 gap-4">
                <div class="rounded-lg border p-4">
                  <p class="text-sm text-muted-foreground">用户总数</p>
                  <p class="text-2xl font-bold mt-1">12,345</p>
                </div>
                <div class="rounded-lg border p-4">
                  <p class="text-sm text-muted-foreground">今日访问</p>
                  <p class="text-2xl font-bold mt-1">1,234</p>
                </div>
                <div class="rounded-lg border p-4">
                  <p class="text-sm text-muted-foreground">活跃用户</p>
                  <p class="text-2xl font-bold mt-1">8,901</p>
                </div>
              </div>
            </div>
            <template #footer>
              &copy; 2026 管理系统
            </template>
          </EAdminLayout>
        </div>
      </DemoBlock>
    </section>

    <section id="collapsed">
      <DemoBlock
        title="折叠侧边栏"
        description="默认折叠状态的布局，通过顶栏汉堡按钮切换"
      >
        <div class="h-[500px] rounded-lg border overflow-hidden">
          <EAdminLayout
            v-model:active-key="activeKey"
            title="后台"
            :menu-items="menuItems"
            :collapsed="true"
            @menu-select="handleMenuSelect"
          >
            <div class="flex items-center justify-center h-full text-muted-foreground">
              <p>折叠状态下的布局，点击左上角按钮展开侧边栏</p>
            </div>
          </EAdminLayout>
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
