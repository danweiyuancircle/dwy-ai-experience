<script setup lang="ts">
import { ref } from 'vue'
import { ChevronsUpDown } from 'lucide-vue-next'
import DemoBlock from '../components/DemoBlock.vue'
import ComponentDoc from '../components/ComponentDoc.vue'
import PropsTable from '../components/PropsTable.vue'
import EventsTable from '../components/EventsTable.vue'
import SlotsTable from '../components/SlotsTable.vue'

const isOpen = ref(false)
const disabledOpen = ref(false)

const tocItems = [
  { id: 'usage', label: '使用场景' },
  { id: 'basic', label: '基础折叠' },
  { id: 'disabled', label: '禁用状态' },
  { id: 'props', label: 'Props' },
  { id: 'events', label: 'Events' },
  { id: 'slots', label: 'Slots' },
]

const propsData = [
  { name: 'modelValue', type: 'boolean', default: 'false', description: '控制折叠/展开状态，支持 v-model' },
  { name: 'disabled', type: 'boolean', default: 'false', description: '是否禁用折叠交互' },
  { name: 'class', type: 'string', description: '自定义 CSS 类名' },
]

const eventsData = [
  { name: 'update:modelValue', params: '(value: boolean)', description: '折叠/展开状态改变时触发' },
]

const slotsData = [
  { name: 'trigger', description: '触发器内容，点击后切换折叠状态' },
  { name: 'default', description: '可折叠的内容区域' },
]
</script>

<template>
  <ComponentDoc
    title="Collapsible 折叠面板"
    description="可折叠/展开的内容区域，通过 v-model 控制状态，支持禁用。适用于需要按需显示的辅助内容。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">适用于信息密度高但非核心内容可隐藏的场景，如代码块展开/收起、高级筛选条件、FAQ 问答折叠等。与 Accordion 的区别在于 Collapsible 是单个独立的折叠单元，不存在排他性展开。</p>
    </section>

    <section id="basic">
      <DemoBlock
        title="基础折叠"
        description="通过 v-model 双向绑定折叠状态，点击触发器切换内容显示"
        code='<ECollapsible v-model="isOpen">
  <template #trigger>
    <EButton variant="ghost">
      显示更多 <ChevronsUpDown class="size-4" />
    </EButton>
  </template>
  <div class="p-4 border rounded-lg mt-2">
    折叠内容
  </div>
</ECollapsible>'
      >
        <ECollapsible v-model="isOpen" class="w-full max-w-sm space-y-2">
          <template #trigger>
            <div class="flex items-center justify-between">
              <h4 class="text-sm font-semibold">@dwydev/eui 包含 3 个文件</h4>
              <EButton variant="ghost" size="sm">
                <ChevronsUpDown class="size-4" />
              </EButton>
            </div>
          </template>
          <div class="rounded-md border px-4 py-2 text-sm font-mono">src/index.ts</div>
          <div class="space-y-2">
            <div class="rounded-md border px-4 py-2 text-sm font-mono">src/components/button/index.ts</div>
            <div class="rounded-md border px-4 py-2 text-sm font-mono">src/utils/cn.ts</div>
          </div>
        </ECollapsible>
      </DemoBlock>
    </section>

    <section id="disabled">
      <DemoBlock
        title="禁用状态"
        description="设置 disabled 后无法切换折叠状态"
        code='<ECollapsible v-model="disabledOpen" disabled>
  ...
</ECollapsible>'
      >
        <ECollapsible v-model="disabledOpen" disabled class="w-full max-w-sm space-y-2">
          <template #trigger>
            <EButton variant="ghost" size="sm" disabled>
              <span class="text-sm">禁用状态，无法展开</span>
              <ChevronsUpDown class="size-4" />
            </EButton>
          </template>
          <div class="rounded-md border px-4 py-2 text-sm">这段内容不会显示</div>
        </ECollapsible>
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
