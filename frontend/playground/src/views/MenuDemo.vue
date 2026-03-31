<script setup lang="ts">
import { ref } from 'vue'
import DemoBlock from '../components/DemoBlock.vue'

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
</script>

<template>
  <div class="max-w-3xl">
    <h1 class="text-2xl font-bold mb-2">Menu 菜单</h1>
    <p class="text-muted-foreground mb-6">侧边导航菜单组件，支持子菜单、禁用项和折叠状态。</p>

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
  </div>
</template>
