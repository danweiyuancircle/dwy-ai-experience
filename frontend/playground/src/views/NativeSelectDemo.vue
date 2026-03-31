<script setup lang="ts">
import { ref } from 'vue'
import DemoBlock from '../components/DemoBlock.vue'
import ComponentDoc from '../components/ComponentDoc.vue'
import PropsTable from '../components/PropsTable.vue'
import EventsTable from '../components/EventsTable.vue'
import SlotsTable from '../components/SlotsTable.vue'

const basicValue = ref<string | number | undefined>(undefined)

const options = [
  { label: '北京', value: 'beijing' },
  { label: '上海', value: 'shanghai' },
  { label: '广州', value: 'guangzhou' },
  { label: '深圳', value: 'shenzhen' },
  { label: '杭州', value: 'hangzhou' },
]

const tocItems = [
  { id: 'usage', label: '使用场景' },
  { id: 'basic', label: '基础用法' },
  { id: 'disabled', label: '禁用状态' },
  { id: 'props', label: 'Props' },
  { id: 'events', label: 'Events' },
]

const propsData = [
  { name: 'modelValue / v-model', type: 'string | number | string[] | number[]', default: '—', description: '绑定值' },
  { name: 'options', type: 'SelectOption[]', default: '[]', description: '选项列表，每项包含 label 和 value' },
  { name: 'placeholder', type: 'string', default: '—', description: '占位文本' },
  { name: 'disabled', type: 'boolean', default: 'false', description: '是否禁用' },
  { name: 'class', type: 'string', default: '—', description: '自定义 CSS 类名' },
]

const eventsData = [
  { name: 'update:modelValue', params: '(value: string | number)', description: 'v-model 绑定值变化时触发' },
  { name: 'change', params: '(event: Event)', description: '选中值改变时触发（原生 change 事件）' },
]

const slotsData = [
  { name: 'default', description: '无默认插槽' },
]
</script>

<template>
  <ComponentDoc
    title="NativeSelect 原生选择器"
    description="基于原生 select 元素的选择器，轻量且无障碍友好。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">适用于选项较少、不需要搜索过滤的简单选择场景。基于浏览器原生 select 元素实现，具有天然的无障碍支持和移动端适配，渲染性能最优。</p>
    </section>

    <section id="basic">
      <DemoBlock
        title="基础用法"
        description="通过 options 提供选项列表，v-model 绑定选中值"
        code='<ENativeSelect v-model="value" :options="options" placeholder="请选择城市" />'
      >
        <div class="space-y-2 max-w-sm">
          <ENativeSelect v-model="basicValue" :options="options" placeholder="请选择城市" />
          <p class="text-sm text-muted-foreground">选中值：{{ basicValue ?? '（未选择）' }}</p>
        </div>
      </DemoBlock>
    </section>

    <section id="disabled">
      <DemoBlock
        title="禁用状态"
        description="设置 disabled 禁止交互"
        code='<ENativeSelect :options="options" disabled placeholder="禁用状态" />'
      >
        <div class="max-w-sm">
          <ENativeSelect :options="options" disabled placeholder="禁用状态" />
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
