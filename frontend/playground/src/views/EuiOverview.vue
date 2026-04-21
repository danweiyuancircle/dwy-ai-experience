<script setup lang="ts">
const stats = [
  { label: '组件数', value: 91, suffix: '+' },
  { label: 'Composables', value: 6, suffix: '' },
  { label: '主题色', value: 7, suffix: '' },
]

const quickLinks = [
  { name: 'Button 按钮', path: '/eui/button', desc: '6 种变体，3 种尺寸，支持 loading 和图标' },
  { name: 'Form 表单', path: '/eui/form', desc: '完整表单验证，基于 Zod schema' },
  { name: 'Table 表格', path: '/eui/table', desc: '排序、选择、自定义列渲染' },
  { name: 'Dialog 对话框', path: '/eui/dialog', desc: '对话框组件，支持拖拽和全屏' },
  { name: 'Select 选择器', path: '/eui/select', desc: '单选、分组、可搜索、可清除' },
  { name: '业务组件', path: '/eui/business', desc: 'EDataPage、EFormDialog、EConfirmDialog' },
]

const features = [
  { title: 'Tailwind CSS v4', desc: '基于最新 Tailwind CSS 4，原生 CSS 变量，按需编译' },
  { title: 'TypeScript', desc: '完整的 TypeScript 类型支持，Composition API 设计' },
  { title: '暗色模式', desc: '内置 7 种主题色 + 深浅模式切换，CSS 变量驱动' },
  { title: 'Reka-ui 无障碍', desc: '基于 Reka UI 无障碍原语构建，符合 WAI-ARIA 标准' },
]

const categories = [
  { label: '基础组件', count: 12, path: '/eui/button' },
  { label: '表单组件', count: 18, path: '/eui/input' },
  { label: '数据展示', count: 15, path: '/eui/table' },
  { label: '导航组件', count: 10, path: '/eui/tabs' },
  { label: '反馈组件', count: 8, path: '/eui/dialog' },
  { label: '业务组件', count: 6, path: '/eui/business' },
]
</script>

<template>
  <div class="max-w-4xl">
    <!-- Header -->
    <div class="mb-8">
      <h1 class="text-3xl font-bold mb-2">@dwydev/eui</h1>
      <p class="text-muted-foreground text-lg">
        Vue 3 组件库 — 基于 Reka-ui + shadcn-vue 设计风格 + Element Plus 式 API
      </p>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-3 gap-4 mb-8">
      <div v-for="stat in stats" :key="stat.label" class="border rounded-lg p-4 text-center">
        <EStatistic :title="stat.label" :value="stat.value" :suffix="stat.suffix" />
      </div>
    </div>

    <!-- Install -->
    <div class="mb-8">
      <h2 class="text-xl font-semibold mb-4">安装</h2>
      <ECard>
        <pre class="text-sm font-mono bg-muted rounded-md p-4 overflow-x-auto"><code>pnpm add @dwydev/eui

# 全局注册
import { createApp } from 'vue'
import EUI from '@dwydev/eui'
import '@dwydev/eui/theme'

const app = createApp(App)
app.use(EUI)</code></pre>
      </ECard>
    </div>

    <!-- Categories -->
    <div class="mb-8">
      <h2 class="text-xl font-semibold mb-4">组件分类</h2>
      <div class="grid grid-cols-3 gap-4">
        <router-link
          v-for="cat in categories"
          :key="cat.label"
          :to="cat.path"
          class="border rounded-lg p-4 hover:bg-accent transition-colors block"
        >
          <div class="flex items-center justify-between mb-1">
            <div class="text-2xl font-bold">{{ cat.count }}+</div>
            <EBadge variant="secondary">{{ cat.label }}</EBadge>
          </div>
        </router-link>
      </div>
    </div>

    <!-- Quick Links -->
    <div class="mb-8">
      <h2 class="text-xl font-semibold mb-4">快速开始</h2>
      <div class="grid grid-cols-2 gap-3">
        <router-link
          v-for="link in quickLinks"
          :key="link.path"
          :to="link.path"
          class="block"
        >
          <ECard class="h-full hover:border-primary/50 transition-colors cursor-pointer">
            <div class="font-medium mb-1">{{ link.name }}</div>
            <div class="text-sm text-muted-foreground">{{ link.desc }}</div>
          </ECard>
        </router-link>
      </div>
    </div>

    <!-- Features -->
    <div>
      <h2 class="text-xl font-semibold mb-4">特性</h2>
      <div class="grid grid-cols-2 gap-3">
        <ECard v-for="feature in features" :key="feature.title">
          <div class="font-medium mb-1">{{ feature.title }}</div>
          <div class="text-sm text-muted-foreground">{{ feature.desc }}</div>
        </ECard>
      </div>
    </div>
  </div>
</template>
