<script setup lang="ts">
import DemoBlock from '../components/DemoBlock.vue'

const basicItems = [
  { label: '首页', href: '/' },
  { label: '用户管理', href: '/users' },
  { label: '用户详情' },
]

const longItems = [
  { label: '首页', href: '/' },
  { label: '系统管理', href: '/system' },
  { label: '权限配置', href: '/system/permissions' },
  { label: '角色列表', href: '/system/permissions/roles' },
  { label: '编辑角色' },
]
</script>

<template>
  <div class="max-w-3xl">
    <h1 class="text-2xl font-bold mb-2">Breadcrumb 面包屑</h1>
    <p class="text-muted-foreground mb-6">页面导航路径组件，帮助用户了解当前位置。</p>

    <DemoBlock
      title="基础面包屑"
      description="使用 items 数组定义面包屑路径"
      code='<EBreadcrumb :items="[
  { label: &apos;首页&apos;, href: &apos;/&apos; },
  { label: &apos;用户管理&apos;, href: &apos;/users&apos; },
  { label: &apos;用户详情&apos; },
]" />'
    >
      <EBreadcrumb :items="basicItems" />
    </DemoBlock>

    <DemoBlock
      title="多级路径"
      description="支持任意层级的路径导航"
    >
      <EBreadcrumb :items="longItems" />
    </DemoBlock>

    <DemoBlock
      title="自定义分隔符"
      description="通过 separator 自定义路径分隔符"
      code='<EBreadcrumb :items="items" separator=">" />'
    >
      <div class="space-y-3">
        <EBreadcrumb :items="basicItems" separator=">" />
        <EBreadcrumb :items="basicItems" separator="|" />
        <EBreadcrumb :items="basicItems" separator="·" />
      </div>
    </DemoBlock>
  </div>
</template>
