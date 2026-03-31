<script setup lang="ts">
import { ref } from 'vue'
import DemoBlock from '../components/DemoBlock.vue'

const lastSelected = ref('')

const basicItems = [
  { key: 'edit', label: '编辑' },
  { key: 'copy', label: '复制' },
  { key: 'paste', label: '粘贴' },
  { key: 'delete', label: '删除', divided: true, variant: 'destructive' as const },
]

const userItems = [
  { key: 'profile', label: '个人中心' },
  { key: 'settings', label: '账号设置' },
  {
    key: 'theme',
    label: '主题切换',
    children: [
      { key: 'light', label: '浅色模式' },
      { key: 'dark', label: '深色模式' },
      { key: 'system', label: '跟随系统' },
    ],
  },
  { key: 'logout', label: '退出登录', divided: true, variant: 'destructive' as const },
]

const actionItems = [
  { key: 'export-csv', label: '导出 CSV' },
  { key: 'export-excel', label: '导出 Excel' },
  { key: 'export-pdf', label: '导出 PDF' },
  { key: 'import', label: '批量导入', divided: true },
  { key: 'delete-all', label: '清空数据', variant: 'destructive' as const, disabled: true },
]
</script>

<template>
  <div class="max-w-3xl">
    <h1 class="text-2xl font-bold mb-2">Dropdown 下拉菜单</h1>
    <p class="text-muted-foreground mb-6">下拉操作菜单，支持子菜单、分隔线、危险项和禁用项。</p>

    <DemoBlock
      title="基础下拉菜单"
      description="点击触发器弹出操作菜单"
      code='<EDropdown :items="items" @select="onSelect">
  <EButton variant="outline">操作</EButton>
</EDropdown>'
    >
      <div class="flex items-center gap-4">
        <EDropdown :items="basicItems" @select="key => lastSelected = key">
          <EButton variant="outline">基础操作</EButton>
        </EDropdown>
        <span class="text-sm text-muted-foreground">
          {{ lastSelected ? `已选：${lastSelected}` : '点击按钮打开菜单' }}
        </span>
      </div>
    </DemoBlock>

    <DemoBlock
      title="带子菜单"
      description="菜单项可以包含 children 实现嵌套子菜单"
      code='const items = [
  { key: "theme", label: "主题切换", children: [
    { key: "light", label: "浅色模式" },
    { key: "dark", label: "深色模式" },
  ] },
]'
    >
      <EDropdown :items="userItems" @select="key => lastSelected = key">
        <EButton>用户菜单</EButton>
      </EDropdown>
    </DemoBlock>

    <DemoBlock
      title="操作菜单（含禁用项）"
      description="设置 disabled: true 禁用菜单项"
      code='const items = [
  { key: "export", label: "导出 CSV" },
  { key: "delete", label: "清空数据", disabled: true, variant: "destructive" },
]'
    >
      <EDropdown :items="actionItems" align="end" @select="key => lastSelected = key">
        <EButton variant="outline">数据操作</EButton>
      </EDropdown>
    </DemoBlock>

    <DemoBlock
      title="不同对齐方式"
      description="通过 align 控制菜单对齐位置"
    >
      <div class="flex gap-3">
        <EDropdown :items="basicItems" align="start">
          <EButton variant="outline" size="sm">左对齐</EButton>
        </EDropdown>
        <EDropdown :items="basicItems" align="center">
          <EButton variant="outline" size="sm">居中对齐</EButton>
        </EDropdown>
        <EDropdown :items="basicItems" align="end">
          <EButton variant="outline" size="sm">右对齐</EButton>
        </EDropdown>
      </div>
    </DemoBlock>
  </div>
</template>
