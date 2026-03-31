<script setup lang="ts">
import DemoBlock from '../components/DemoBlock.vue'
import ComponentDoc from '../components/ComponentDoc.vue'
import PropsTable from '../components/PropsTable.vue'
import SlotsTable from '../components/SlotsTable.vue'

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

const tocItems = [
  { id: 'usage', label: '使用场景' },
  { id: 'basic', label: '基础面包屑' },
  { id: 'long', label: '多级路径' },
  { id: 'separator', label: '自定义分隔符' },
  { id: 'props', label: 'Props' },
  { id: 'slots', label: 'Slots' },
]

const propsData = [
  { name: 'items', type: 'BreadcrumbItem[]', default: '[]', description: '面包屑路径数组，每项包含 label、href（可选）、icon（可选）' },
  { name: 'separator', type: 'string', default: "'/'", description: '路径分隔符' },
  { name: 'class', type: 'string', default: '-', description: '自定义 CSS 类名' },
]

const slotsData = [
  { name: '-', description: 'EBreadcrumb 不提供自定义插槽，内容由 items 数据驱动渲染' },
]
</script>

<template>
  <ComponentDoc
    title="Breadcrumb 面包屑"
    description="页面导航路径组件，帮助用户了解当前位置。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">适用于多层级页面结构中标识当前位置并提供返回上级路径的快捷方式。常见于后台管理系统的顶部导航区域，配合路由自动生成路径层级。最后一项通常为当前页面，不带链接。</p>
    </section>

    <section id="basic">
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
    </section>

    <section id="long">
      <DemoBlock
        title="多级路径"
        description="支持任意层级的路径导航"
      >
        <EBreadcrumb :items="longItems" />
      </DemoBlock>
    </section>

    <section id="separator">
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
    </section>

    <section id="props">
      <PropsTable :data="propsData" />
    </section>

    <section id="slots">
      <SlotsTable :data="slotsData" />
    </section>
  </ComponentDoc>
</template>
