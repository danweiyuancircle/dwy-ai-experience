<script setup lang="ts">
const stats = [
  { label: '基础组件', count: 12, path: '/button' },
  { label: '表单组件', count: 18, path: '/input' },
  { label: '数据展示', count: 15, path: '/table' },
  { label: '导航组件', count: 10, path: '/tabs' },
  { label: '反馈组件', count: 8, path: '/dialog-drawer' },
  { label: '业务组件', count: 6, path: '/business' },
]

const quickLinks = [
  { name: 'Button 按钮', path: '/button', desc: '6 种变体，3 种尺寸，支持 loading' },
  { name: 'Form 表单', path: '/form', desc: '完整表单验证，基于 Zod' },
  { name: 'Table 表格', path: '/table', desc: '排序、选择、自定义渲染' },
  { name: 'Dialog 对话框', path: '/dialog-drawer', desc: '对话框与抽屉组件' },
  { name: 'Select 选择器', path: '/select', desc: '单选、分组、可清除' },
  { name: '业务组件', path: '/business', desc: 'EDataPage、EFormDialog、EConfirmDialog' },
]
</script>

<template>
  <div class="max-w-4xl">
    <div class="mb-8">
      <h1 class="text-3xl font-bold mb-2">EUI 组件库预览</h1>
      <p class="text-muted-foreground text-lg">
        基于 Vue 3 + Tailwind CSS v4 构建的现代化 UI 组件库，提供 91+ 个可复用组件。
      </p>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-3 gap-4 mb-8">
      <router-link
        v-for="stat in stats"
        :key="stat.label"
        :to="stat.path"
        class="border rounded-lg p-4 hover:bg-accent transition-colors block"
      >
        <div class="text-2xl font-bold mb-1">{{ stat.count }}+</div>
        <div class="text-sm text-muted-foreground">{{ stat.label }}</div>
      </router-link>
    </div>

    <!-- Quick Links -->
    <div class="mb-8">
      <h2 class="text-xl font-semibold mb-4">快速开始</h2>
      <div class="grid grid-cols-2 gap-3">
        <router-link
          v-for="link in quickLinks"
          :key="link.path"
          :to="link.path"
          class="border rounded-lg p-4 hover:bg-accent transition-colors block"
        >
          <div class="font-medium mb-1">{{ link.name }}</div>
          <div class="text-sm text-muted-foreground">{{ link.desc }}</div>
        </router-link>
      </div>
    </div>

    <!-- Features -->
    <div>
      <h2 class="text-xl font-semibold mb-4">特性</h2>
      <div class="grid grid-cols-2 gap-3">
        <div class="border rounded-lg p-4">
          <div class="font-medium mb-1">Vue 3 + TypeScript</div>
          <div class="text-sm text-muted-foreground">完整的 TypeScript 类型支持，Composition API 设计</div>
        </div>
        <div class="border rounded-lg p-4">
          <div class="font-medium mb-1">Tailwind CSS v4</div>
          <div class="text-sm text-muted-foreground">基于最新 Tailwind CSS，支持暗色模式</div>
        </div>
        <div class="border rounded-lg p-4">
          <div class="font-medium mb-1">Reka UI 原语</div>
          <div class="text-sm text-muted-foreground">基于 Reka UI 无障碍原语构建，符合 WAI-ARIA</div>
        </div>
        <div class="border rounded-lg p-4">
          <div class="font-medium mb-1">业务场景组件</div>
          <div class="text-sm text-muted-foreground">包含 EDataPage、EFormDialog 等开箱即用的业务组件</div>
        </div>
      </div>
    </div>
  </div>
</template>
