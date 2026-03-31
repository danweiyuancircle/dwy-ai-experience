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

const radioValue = ref('vue')
const radioValueVertical = ref('react')
const radioDisabled = ref('angular')
const radioButtonValue = ref('vue')

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
  { id: 'checkbox-disabled', label: '复选框禁用' },
  { id: 'checkbox-group', label: '复选框组' },
  { id: 'radio-horizontal', label: 'Radio 水平' },
  { id: 'radio-vertical', label: 'Radio 垂直' },
  { id: 'radio-disabled', label: 'Radio 禁用' },
  { id: 'radio-button', label: '按钮式单选' },
  { id: 'checkbox-props', label: 'Checkbox Props' },
  { id: 'checkbox-events', label: 'Checkbox Events' },
  { id: 'radio-props', label: 'Radio Props' },
  { id: 'radio-events', label: 'Radio Events' },
  { id: 'slots', label: 'Slots' },
]

const checkboxPropsData = [
  { name: 'modelValue', type: "boolean | (string | number)[]", description: '绑定值，单选模式为布尔值，组模式为选中值数组' },
  { name: 'label', type: 'string', description: '复选框旁的文本标签' },
  { name: 'disabled', type: 'boolean', default: 'false', description: '是否禁用' },
  { name: 'indeterminate', type: 'boolean', default: 'false', description: '是否为不确定状态（半选）' },
  { name: 'options', type: 'Option[]', description: '选项数组，提供后渲染为复选框组' },
  { name: 'direction', type: "'horizontal' | 'vertical'", default: "'horizontal'", description: '组模式下的排列方向' },
  { name: 'border', type: 'boolean', default: 'false', description: '是否显示边框样式' },
  { name: 'class', type: 'string', description: '自定义 CSS 类名' },
]

const checkboxEventsData = [
  { name: 'update:modelValue', params: '(value: boolean | (string | number)[])', description: '值变化时触发（用于 v-model）' },
  { name: 'change', params: '(value: boolean | (string | number)[])', description: '值变化时触发' },
]

const radioPropsData = [
  { name: 'modelValue', type: 'string | number', description: '绑定值' },
  { name: 'options', type: 'Option[]', description: '选项数组' },
  { name: 'disabled', type: 'boolean', default: 'false', description: '是否禁用整个单选组' },
  { name: 'direction', type: "'horizontal' | 'vertical'", default: "'horizontal'", description: '排列方向' },
  { name: 'optionType', type: "'default' | 'button'", default: "'default'", description: '渲染样式，button 为分段按钮组' },
  { name: 'border', type: 'boolean', default: 'false', description: '是否显示边框样式（仅 default 模式）' },
  { name: 'size', type: "'sm' | 'default' | 'lg'", default: "'default'", description: '尺寸' },
  { name: 'class', type: 'string', description: '自定义 CSS 类名' },
]

const radioEventsData = [
  { name: 'update:modelValue', params: '(value: string | number)', description: '选中值变化时触发（用于 v-model）' },
  { name: 'change', params: '(value: string | number)', description: '选中值变化时触发' },
]

const slotsData = [
  { name: 'default', description: '自定义标签内容（Checkbox 单选模式）' },
]
</script>

<template>
  <ComponentDoc
    title="Checkbox & Radio 复选框与单选框"
    description="复选框和单选框组件，支持单选/多选、分组、按钮样式、禁用状态等场景。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">Checkbox 适用于多选场景，如勾选同意条款、批量选择列表项、权限配置等；Radio 适用于单选场景，如性别选择、支付方式选择、配置项切换等。按钮式单选（optionType="button"）适合选项较少且需要直观展示的场景。</p>
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

    <section id="radio-horizontal">
      <DemoBlock
        title="Radio 单选（水平）"
        description="通过 options 数组渲染单选组，默认水平排列"
        code='<ERadio v-model="value" :options="options" />'
      >
        <div class="space-y-3">
          <ERadio v-model="radioValue" :options="frameworks" />
          <p class="text-sm text-muted-foreground">当前选择：{{ radioValue }}</p>
        </div>
      </DemoBlock>
    </section>

    <section id="radio-vertical">
      <DemoBlock
        title="Radio 单选（垂直）"
        description="设置 direction='vertical' 垂直排列"
        code='<ERadio v-model="value" :options="options" direction="vertical" />'
      >
        <div class="space-y-3">
          <ERadio v-model="radioValueVertical" :options="frameworks" direction="vertical" />
          <p class="text-sm text-muted-foreground">当前选择：{{ radioValueVertical }}</p>
        </div>
      </DemoBlock>
    </section>

    <section id="radio-disabled">
      <DemoBlock
        title="Radio 禁用状态"
        description="设置 disabled 禁用整个单选组"
        code='<ERadio v-model="value" :options="options" :disabled="true" />'
      >
        <ERadio v-model="radioDisabled" :options="frameworks" :disabled="true" />
      </DemoBlock>
    </section>

    <section id="radio-button">
      <DemoBlock
        title="按钮式单选"
        description="设置 option-type=&quot;button&quot; 以按钮样式展示单选组"
        code='<ERadio v-model="val" :options="options" option-type="button" />'
      >
        <div class="space-y-3">
          <ERadio v-model="radioButtonValue" :options="frameworks" option-type="button" />
          <p class="text-sm text-muted-foreground">当前选择：{{ radioButtonValue }}</p>
        </div>
      </DemoBlock>
    </section>

    <section id="checkbox-props">
      <h2 class="text-lg font-semibold mb-3">Checkbox Props</h2>
      <PropsTable :data="checkboxPropsData" />
    </section>

    <section id="checkbox-events">
      <h2 class="text-lg font-semibold mb-3">Checkbox Events</h2>
      <EventsTable :data="checkboxEventsData" />
    </section>

    <section id="radio-props">
      <h2 class="text-lg font-semibold mb-3">Radio Props</h2>
      <PropsTable :data="radioPropsData" />
    </section>

    <section id="radio-events">
      <h2 class="text-lg font-semibold mb-3">Radio Events</h2>
      <EventsTable :data="radioEventsData" />
    </section>

    <section id="slots">
      <SlotsTable :data="slotsData" />
    </section>
  </ComponentDoc>
</template>
