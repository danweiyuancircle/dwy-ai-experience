<script setup lang="ts">
import { ref } from 'vue'
import DemoBlock from '../components/DemoBlock.vue'
import ComponentDoc from '../components/ComponentDoc.vue'
import PropsTable from '../components/PropsTable.vue'
import EventsTable from '../components/EventsTable.vue'
import SlotsTable from '../components/SlotsTable.vue'

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

const tocItems = [
  { id: 'usage', label: '使用场景' },
  { id: 'basic', label: '基础下拉菜单' },
  { id: 'submenu', label: '带子菜单' },
  { id: 'disabled-item', label: '含禁用项' },
  { id: 'align', label: '不同对齐方式' },
  { id: 'hover', label: '悬浮触发' },
  { id: 'split', label: '分裂按钮' },
  { id: 'props', label: 'Props' },
  { id: 'events', label: 'Events' },
  { id: 'slots', label: 'Slots' },
]

const propsData = [
  { name: 'items', type: 'DropdownMenuItem[]', default: '[]', description: '菜单项数组，支持 children 嵌套子菜单' },
  { name: 'side', type: "'top' | 'right' | 'bottom' | 'left'", default: "'bottom'", description: '菜单弹出方向' },
  { name: 'align', type: "'start' | 'center' | 'end'", default: "'start'", description: '菜单对齐方式' },
  { name: 'sideOffset', type: 'number', default: '4', description: '菜单与触发器的距离（px）' },
  { name: 'trigger', type: "'click' | 'hover'", default: "'click'", description: '菜单触发方式' },
  { name: 'splitButton', type: 'boolean', default: 'false', description: '是否显示为分裂按钮（操作按钮 + 下拉箭头）' },
  { name: 'buttonText', type: 'string', default: '-', description: '分裂按钮模式下的按钮文字' },
  { name: 'buttonVariant', type: "'default' | 'destructive' | 'outline' | 'secondary' | 'ghost' | 'link'", default: "'default'", description: '分裂按钮的变体样式' },
  { name: 'class', type: 'string', default: '-', description: '自定义 CSS 类名' },
]

const eventsData = [
  { name: 'select', params: '(key: string)', description: '选中菜单项时触发' },
  { name: 'click', params: '()', description: '分裂按钮模式下点击主按钮时触发' },
]

const slotsData = [
  { name: 'default', description: '触发器内容（按钮等），点击/悬浮触发下拉菜单' },
]
</script>

<template>
  <ComponentDoc
    title="Dropdown 下拉菜单"
    description="下拉操作菜单，支持子菜单、分隔线、危险项和禁用项。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">适用于在有限空间内提供多个操作选项，如表格行操作菜单、用户头像下拉菜单、导出数据格式选择等。支持嵌套子菜单、分隔线分组、危险操作高亮、禁用项、分裂按钮等模式。</p>
    </section>

    <section id="basic">
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
    </section>

    <section id="submenu">
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
    </section>

    <section id="disabled-item">
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
    </section>

    <section id="align">
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
    </section>

    <section id="hover">
      <DemoBlock
        title="悬浮触发"
        description="设置 trigger=&quot;hover&quot; 鼠标悬浮时展开菜单"
        code='<EDropdown :items="items" trigger="hover">
  <EButton variant="outline">悬浮打开</EButton>
</EDropdown>'
      >
        <EDropdown :items="basicItems" trigger="hover" @select="key => lastSelected = key">
          <EButton variant="outline">悬浮打开</EButton>
        </EDropdown>
      </DemoBlock>
    </section>

    <section id="split">
      <DemoBlock
        title="分裂按钮"
        description="设置 split-button 将触发器分为操作按钮和下拉箭头两部分"
        code='<EDropdown :items="items" split-button button-text="操作" />'
      >
        <EDropdown
          :items="actionItems"
          split-button
          button-text="操作"
          @select="key => lastSelected = key"
        />
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
