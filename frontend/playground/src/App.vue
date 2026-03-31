<script setup lang="ts">
import { useRoute } from 'vue-router'
import { useTheme } from '@danweiyuan/eui'
import { Toaster as EToastRoot } from 'vue-sonner'
import { Sun, Moon } from 'lucide-vue-next'

const route = useRoute()
const { isDark, toggleDark, colorTheme, setColorTheme } = useTheme()

const themes = [
  { name: 'neutral', color: '#171717', label: 'Neutral' },
  { name: 'blue', color: '#2563eb', label: 'Blue' },
  { name: 'green', color: '#16a34a', label: 'Green' },
  { name: 'rose', color: '#e11d48', label: 'Rose' },
  { name: 'orange', color: '#ea580c', label: 'Orange' },
  { name: 'violet', color: '#7c3aed', label: 'Violet' },
  { name: 'slate', color: '#475569', label: 'Slate' },
]

const categories = [
  {
    title: '基础 Basic',
    items: [
      { name: 'Button 按钮', path: '/button' },
      { name: 'Badge 徽标', path: '/alert-badge' },
      { name: 'Alert 提示', path: '/alert-badge' },
      { name: 'Card 卡片', path: '/card' },
      { name: 'Avatar 头像', path: '/avatar' },
      { name: 'Typography 排版', path: '/misc' },
    ],
  },
  {
    title: '表单 Form',
    items: [
      { name: 'Input 输入框', path: '/input' },
      { name: 'Select 选择器', path: '/select' },
      { name: 'Checkbox & Radio', path: '/checkbox-radio' },
      { name: 'Switch 开关', path: '/switch' },
      { name: 'Slider 滑块', path: '/slider' },
      { name: 'Rate 评分', path: '/rate' },
      { name: 'DatePicker 日期', path: '/date-time' },
      { name: 'TagsInput 标签', path: '/tags-input' },
      { name: 'Upload 上传', path: '/upload' },
      { name: 'Form 表单', path: '/form' },
    ],
  },
  {
    title: '数据展示 Data',
    items: [
      { name: 'Table 表格', path: '/table' },
      { name: 'Descriptions 描述', path: '/descriptions' },
      { name: 'Statistic 统计', path: '/statistic' },
      { name: 'Timeline 时间线', path: '/timeline' },
      { name: 'Tree 树形控件', path: '/tree' },
      { name: 'Progress 进度条', path: '/progress' },
      { name: 'Skeleton 骨架', path: '/skeleton' },
      { name: 'Carousel 走马灯', path: '/carousel' },
    ],
  },
  {
    title: '导航 Navigation',
    items: [
      { name: 'Tabs 标签页', path: '/tabs' },
      { name: 'Menu 菜单', path: '/menu' },
      { name: 'Breadcrumb 面包屑', path: '/breadcrumb' },
      { name: 'Pagination 分页', path: '/pagination' },
      { name: 'Dropdown 下拉菜单', path: '/dropdown' },
      { name: 'Stepper 步骤条', path: '/stepper' },
    ],
  },
  {
    title: '反馈 Feedback',
    items: [
      { name: 'Dialog 对话框', path: '/dialog-drawer' },
      { name: 'Drawer 抽屉', path: '/dialog-drawer' },
      { name: 'Toast 轻提示', path: '/toast' },
      { name: 'Tooltip 文字提示', path: '/tooltip-popover' },
      { name: 'Popover 气泡卡片', path: '/tooltip-popover' },
    ],
  },
  {
    title: '其他 Other',
    items: [
      { name: 'Accordion 手风琴', path: '/accordion' },
      { name: 'Transfer 穿梭框', path: '/transfer' },
      { name: 'Misc 杂项', path: '/misc' },
      { name: '业务组件', path: '/business' },
    ],
  },
]
</script>

<template>
  <div class="flex h-screen">
    <!-- Sidebar -->
    <aside class="w-64 border-r overflow-y-auto bg-background shrink-0">
      <div class="p-4 border-b">
        <div class="flex items-center justify-between">
          <router-link to="/" class="block">
            <h1 class="text-lg font-bold">EUI Preview</h1>
            <p class="text-xs text-muted-foreground">91+ Components</p>
          </router-link>
          <button @click="toggleDark" class="p-2 rounded-md hover:bg-accent transition-colors" title="Toggle dark mode">
            <Sun v-if="isDark" class="size-4" />
            <Moon v-else class="size-4" />
          </button>
        </div>
        <div class="flex gap-1.5 mt-2">
          <button
            v-for="t in themes"
            :key="t.name"
            @click="setColorTheme(t.name)"
            :class="['size-5 rounded-full border-2 transition-all', colorTheme === t.name ? 'border-foreground scale-110' : 'border-transparent']"
            :style="{ background: t.color }"
            :title="t.label"
          />
        </div>
      </div>
      <nav class="p-2">
        <div v-for="cat in categories" :key="cat.title" class="mb-4">
          <h3 class="px-3 py-1 text-xs font-semibold text-muted-foreground uppercase tracking-wider">{{ cat.title }}</h3>
          <router-link
            v-for="item in cat.items"
            :key="item.path + item.name"
            :to="item.path"
            class="block px-3 py-1.5 rounded-md text-sm hover:bg-accent transition-colors"
            active-class="bg-accent text-accent-foreground font-medium"
          >
            {{ item.name }}
          </router-link>
        </div>
      </nav>
    </aside>
    <!-- Main Content -->
    <main class="flex-1 overflow-y-auto p-8">
      <router-view />
    </main>
    <EToastRoot position="top-right" :rich-colors="true" />
  </div>
</template>
