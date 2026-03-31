<script setup lang="ts">
import { ref } from 'vue'
import DemoBlock from '../components/DemoBlock.vue'
import ComponentDoc from '../components/ComponentDoc.vue'
import PropsTable from '../components/PropsTable.vue'
import EventsTable from '../components/EventsTable.vue'
import SlotsTable from '../components/SlotsTable.vue'

const basicValue = ref<string | number | undefined>(undefined)

const options = [
  { label: 'React', value: 'react' },
  { label: 'Vue', value: 'vue' },
  { label: 'Angular', value: 'angular' },
  { label: 'Svelte', value: 'svelte' },
  { label: 'Solid', value: 'solid' },
  { label: 'Preact', value: 'preact' },
]

const tocItems = [
  { id: 'usage', label: '使用场景' },
  { id: 'basic', label: '基础用法' },
  { id: 'disabled', label: '禁用状态' },
  { id: 'props', label: 'Props' },
  { id: 'events', label: 'Events' },
]

const propsData = [
  { name: 'modelValue / v-model', type: 'string | number', default: '—', description: '绑定值' },
  { name: 'options', type: 'Option[]', default: '[]', description: '选项列表，每项包含 label 和 value' },
  { name: 'placeholder', type: 'string', default: '—', description: '占位文本' },
  { name: 'disabled', type: 'boolean', default: 'false', description: '是否禁用' },
  { name: 'emptyText', type: 'string', default: '—', description: '无匹配选项时显示的文本' },
  { name: 'class', type: 'string', default: '—', description: '自定义 CSS 类名' },
]

const eventsData = [
  { name: 'update:modelValue', params: '(value: string | number | undefined)', description: 'v-model 绑定值变化时触发' },
  { name: 'change', params: '(value: string | number | undefined)', description: '选中值改变时触发' },
]

const slotsData = [
  { name: 'default', description: '无默认插槽' },
]
</script>

<template>
  <ComponentDoc
    title="Combobox 组合框"
    description="可输入搜索的下拉选择器，支持从候选项中选择或输入自定义值。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">适用于选项数量较多、需要搜索过滤的选择场景。与 Select 不同，Combobox 允许用户输入关键字过滤候选项，操作更高效。</p>
    </section>

    <section id="basic">
      <DemoBlock
        title="基础用法"
        description="通过 options 提供选项列表，v-model 绑定选中值"
        code='<ECombobox v-model="value" :options="options" placeholder="请选择框架" />'
      >
        <div class="space-y-2 max-w-sm">
          <ECombobox v-model="basicValue" :options="options" placeholder="请选择框架" />
          <p class="text-sm text-muted-foreground">选中值：{{ basicValue ?? '（未选择）' }}</p>
        </div>
      </DemoBlock>
    </section>

    <section id="disabled">
      <DemoBlock
        title="禁用状态"
        description="设置 disabled 禁止交互"
        code='<ECombobox :options="options" disabled placeholder="禁用状态" />'
      >
        <div class="max-w-sm">
          <ECombobox :options="options" disabled placeholder="禁用状态" />
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
