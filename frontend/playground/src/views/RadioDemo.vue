<script setup lang="ts">
import { ref } from 'vue'
import DemoBlock from '../components/DemoBlock.vue'
import ComponentDoc from '../components/ComponentDoc.vue'
import PropsTable from '../components/PropsTable.vue'
import EventsTable from '../components/EventsTable.vue'

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
  { id: 'radio-horizontal', label: '水平排列' },
  { id: 'radio-vertical', label: '垂直排列' },
  { id: 'radio-disabled', label: '禁用状态' },
  { id: 'radio-button', label: '按钮式单选' },
  { id: 'props', label: 'Props' },
  { id: 'events', label: 'Events' },
]

const propsData = [
  { name: 'modelValue', type: 'string | number', description: '绑定值' },
  { name: 'options', type: 'Option[]', description: '选项数组' },
  { name: 'disabled', type: 'boolean', default: 'false', description: '是否禁用整个单选组' },
  { name: 'direction', type: "'horizontal' | 'vertical'", default: "'horizontal'", description: '排列方向' },
  { name: 'optionType', type: "'default' | 'button'", default: "'default'", description: '渲染样式，button 为分段按钮组' },
  { name: 'border', type: 'boolean', default: 'false', description: '是否显示边框样式（仅 default 模式）' },
  { name: 'size', type: "'sm' | 'default' | 'lg'", default: "'default'", description: '尺寸' },
  { name: 'class', type: 'string', description: '自定义 CSS 类名' },
]

const eventsData = [
  { name: 'update:modelValue', params: '(value: string | number)', description: '选中值变化时触发（用于 v-model）' },
  { name: 'change', params: '(value: string | number)', description: '选中值变化时触发' },
]
</script>

<template>
  <ComponentDoc
    title="Radio 单选框"
    description="单选框组件，适用于性别选择、支付方式选择、配置项切换等单选场景。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">Radio 适用于单选场景，如性别选择、支付方式选择、配置项切换等。按钮式单选（optionType="button"）适合选项较少且需要直观展示的场景。</p>
    </section>

    <section id="radio-horizontal">
      <DemoBlock
        title="水平排列"
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
        title="垂直排列"
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
        title="禁用状态"
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

    <section id="props">
      <h2 class="text-lg font-semibold mb-3">Radio Props</h2>
      <PropsTable :data="propsData" />
    </section>

    <section id="events">
      <h2 class="text-lg font-semibold mb-3">Radio Events</h2>
      <EventsTable :data="eventsData" />
    </section>
  </ComponentDoc>
</template>
