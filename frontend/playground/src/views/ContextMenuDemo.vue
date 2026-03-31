<script setup lang="ts">
import { ref } from 'vue'
import { Copy, Scissors, Clipboard, Trash2, FolderOpen, RotateCcw } from 'lucide-vue-next'
import DemoBlock from '../components/DemoBlock.vue'
import ComponentDoc from '../components/ComponentDoc.vue'
import PropsTable from '../components/PropsTable.vue'
import EventsTable from '../components/EventsTable.vue'
import SlotsTable from '../components/SlotsTable.vue'

const selectedKey = ref('')

const menuItems = [
  { key: 'copy', label: '复制', icon: Copy },
  { key: 'cut', label: '剪切', icon: Scissors },
  { key: 'paste', label: '粘贴', icon: Clipboard },
  { key: 'open', label: '打开', icon: FolderOpen, divided: true },
  { key: 'undo', label: '撤销', icon: RotateCcw, disabled: true },
  { key: 'delete', label: '删除', icon: Trash2, variant: 'destructive' as const, divided: true },
]

function handleSelect(key: string) {
  selectedKey.value = key
}

const tocItems = [
  { id: 'usage', label: '使用场景' },
  { id: 'basic', label: '基础右键菜单' },
  { id: 'props', label: 'Props' },
  { id: 'events', label: 'Events' },
  { id: 'slots', label: 'Slots' },
]

const propsData = [
  { name: 'items', type: 'ContextMenuItem[]', default: '[]', description: '菜单项配置数组' },
  { name: 'class', type: 'string', description: '自定义菜单内容区域的 CSS 类名' },
]

const eventsData = [
  { name: 'select', params: '(key: string)', description: '选中菜单项时触发，返回菜单项的 key' },
]

const slotsData = [
  { name: 'default', description: '右键触发区域内容' },
]
</script>

<template>
  <ComponentDoc
    title="ContextMenu 右键菜单"
    description="右键点击触发的上下文菜单，支持图标、分割线、禁用状态和子菜单，适用于文件管理、编辑器等场景。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">适用于需要在特定区域提供上下文操作的场景，如文件列表的右键操作（复制、剪切、删除）、文本编辑器的右键菜单、画布工具的操作选项等。通过配置 items 数组快速生成菜单。</p>
    </section>

    <section id="basic">
      <DemoBlock
        title="基础右键菜单"
        description="在指定区域右键点击弹出上下文菜单，支持图标、分割线、禁用和危险样式"
        code='<EContextMenu :items="menuItems" @select="handleSelect">
  <div class="border border-dashed rounded-lg p-10 text-center">
    在此区域右键点击
  </div>
</EContextMenu>'
      >
        <div class="space-y-3">
          <EContextMenu :items="menuItems" @select="handleSelect">
            <div class="flex h-40 w-full items-center justify-center rounded-lg border border-dashed text-sm text-muted-foreground">
              在此区域右键点击
            </div>
          </EContextMenu>
          <p v-if="selectedKey" class="text-sm text-muted-foreground">
            你选择了: <code class="bg-muted px-1.5 py-0.5 rounded text-xs font-mono">{{ selectedKey }}</code>
          </p>
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
