<script setup lang="ts">
import { ref } from 'vue'
import DemoBlock from '../components/DemoBlock.vue'
import ComponentDoc from '../components/ComponentDoc.vue'
import PropsTable from '../components/PropsTable.vue'
import EventsTable from '../components/EventsTable.vue'
import SlotsTable from '../components/SlotsTable.vue'

const singleCheck = ref(false)
const indeterminate = ref(true)
const disabledCheck = ref(false)
const checkboxGroupValue = ref<string[]>(['vue', 'react'])

const frameworks = [
  { label: 'Vue 3', value: 'vue' },
  { label: 'React', value: 'react' },
  { label: 'Angular', value: 'angular' },
  { label: 'Svelte', value: 'svelte' },
]

const tocItems = [
  { id: 'usage', label: '使用场景' },
  { id: 'checkbox-basic', label: '基础复选框' },
  { id: 'checkbox-indeterminate', label: '不确定状态' },
  { id: 'checkbox-disabled', label: '禁用状态' },
  { id: 'checkbox-group', label: '复选框组' },
  { id: 'props', label: 'Props' },
  { id: 'events', label: 'Events' },
  { id: 'slots', label: 'Slots' },
]

const propsData = [
  { name: 'modelValue', type: "boolean | (string | number)[]", description: '绑定值，单选模式为布尔值，组模式为选中值数组' },
  { name: 'label', type: 'string', description: '复选框旁的文本标签' },
  { name: 'disabled', type: 'boolean', default: 'false', description: '是否禁用' },
  { name: 'indeterminate', type: 'boolean', default: 'false', description: '是否为不确定状态（半选）' },
  { name: 'options', type: 'Option[]', description: '选项数组，提供后渲染为复选框组' },
  { name: 'direction', type: "'horizontal' | 'vertical'", default: "'horizontal'", description: '组模式下的排列方向' },
  { name: 'border', type: 'boolean', default: 'false', description: '是否显示边框样式' },
  { name: 'class', type: 'string', description: '自定义 CSS 类名' },
]

const eventsData = [
  { name: 'update:modelValue', params: '(value: boolean | (string | number)[])', description: '值变化时触发（用于 v-model）' },
  { name: 'change', params: '(value: boolean | (string | number)[])', description: '值变化时触发' },
]

const slotsData = [
  { name: 'default', description: '自定义标签内容（单选模式）' },
]
</script>

<template>
  <ComponentDoc
    title="Checkbox 复选框"
    description="复选框组件，支持单选/多选、分组、不确定状态、禁用等场景。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">Checkbox 适用于多选场景，如勾选同意条款、批量选择列表项、权限配置等。支持单个复选框和复选框组两种模式。</p>
    </section>

    <section id="checkbox-basic">
      <DemoBlock
        title="基础复选框"
        description="单个复选框，支持 label 文本显示"
        code='<ECheckbox v-model="checked" label="同意服务条款" />'
      >
        <div class="space-y-3">
          <ECheckbox v-model="singleCheck" label="同意服务条款" />
          <p class="text-sm text-muted-foreground">当前状态：{{ singleCheck ? '已勾选' : '未勾选' }}</p>
        </div>
      </DemoBlock>
    </section>

    <section id="checkbox-indeterminate">
      <DemoBlock
        title="不确定状态"
        description="通过 indeterminate 属性设置半选状态（常用于全选场景）"
        code='<ECheckbox :indeterminate="true" label="全选（半选状态）" />'
      >
        <ECheckbox v-model="indeterminate" :indeterminate="true" label="全选（半选状态）" />
      </DemoBlock>
    </section>

    <section id="checkbox-disabled">
      <DemoBlock
        title="禁用状态"
        description="disabled 禁用复选框交互"
        code='<ECheckbox :disabled="true" label="禁用（未选）" />
<ECheckbox :modelValue="true" :disabled="true" label="禁用（已选）" />'
      >
        <div class="flex gap-4">
          <ECheckbox v-model="disabledCheck" :disabled="true" label="禁用（未选）" />
          <ECheckbox :modelValue="true" :disabled="true" label="禁用（已选）" />
        </div>
      </DemoBlock>
    </section>

    <section id="checkbox-group">
      <DemoBlock
        title="复选框组"
        description="通过 options 数组渲染复选框组，v-model 绑定已选值数组"
        code='<ECheckbox v-model="checked" :options="options" />'
      >
        <div class="space-y-3">
          <ECheckbox v-model="checkboxGroupValue" :options="frameworks" />
          <p class="text-sm text-muted-foreground">已选：{{ checkboxGroupValue.join(', ') || '(未选择)' }}</p>
        </div>
      </DemoBlock>
    </section>

    <section id="props">
      <h2 class="text-lg font-semibold mb-3">Checkbox Props</h2>
      <PropsTable :data="propsData" />
    </section>

    <section id="events">
      <h2 class="text-lg font-semibold mb-3">Checkbox Events</h2>
      <EventsTable :data="eventsData" />
    </section>

    <section id="slots">
      <h2 class="text-lg font-semibold mb-3">Checkbox Slots</h2>
      <SlotsTable :data="slotsData" />
    </section>
  </ComponentDoc>
</template>
