<script setup lang="ts">
import { ref } from 'vue'
import DemoBlock from '../components/DemoBlock.vue'
import ComponentDoc from '../components/ComponentDoc.vue'
import PropsTable from '../components/PropsTable.vue'
import EventsTable from '../components/EventsTable.vue'
import SlotsTable from '../components/SlotsTable.vue'

const singleValue = ref()
const multipleValues = ref()

const tocItems = [
  { id: 'usage', label: '使用场景' },
  { id: 'basic', label: '基础日历' },
  { id: 'multiple', label: '多选日期' },
  { id: 'props', label: 'Props' },
  { id: 'events', label: 'Events' },
]

const propsData = [
  { name: 'modelValue', type: 'DateValue | DateValue[]', description: '选中的日期值，支持 v-model' },
  { name: 'defaultValue', type: 'DateValue | DateValue[]', description: '默认选中的日期' },
  { name: 'multiple', type: 'boolean', default: 'false', description: '是否允许选择多个日期' },
  { name: 'disabled', type: 'boolean', default: 'false', description: '是否禁用日历' },
  { name: 'readonly', type: 'boolean', default: 'false', description: '是否只读' },
  { name: 'locale', type: 'string', description: "区域设置，如 'zh-CN'、'en-US'" },
  { name: 'minValue', type: 'DateValue', description: '可选日期范围的最小值' },
  { name: 'maxValue', type: 'DateValue', description: '可选日期范围的最大值' },
  { name: 'class', type: 'string', description: '自定义 CSS 类名' },
]

const eventsData = [
  { name: 'update:modelValue', params: '(value: DateValue | DateValue[])', description: '选中日期变化时触发' },
]
</script>

<template>
  <ComponentDoc
    title="Calendar 日历"
    description="日历面板组件，支持单选、多选日期，可配置区域化和日期范围限制。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">适用于需要直接在页面中展示日历面板的场景，如日程管理、考勤打卡、预约系统等。如果需要在输入框中选择日期，请使用 DatePicker 组件。</p>
    </section>

    <section id="basic">
      <DemoBlock
        title="基础日历"
        description="单选模式，点击日期进行选择"
        code='<ECalendar v-model="singleValue" locale="zh-CN" />'
      >
        <div class="space-y-3">
          <ECalendar v-model="singleValue" locale="zh-CN" class="rounded-md border" />
          <p v-if="singleValue" class="text-sm text-muted-foreground">
            选中日期: <code class="bg-muted px-1.5 py-0.5 rounded text-xs font-mono">{{ singleValue }}</code>
          </p>
        </div>
      </DemoBlock>
    </section>

    <section id="multiple">
      <DemoBlock
        title="多选日期"
        description="开启 multiple 属性，可选择多个日期"
        code='<ECalendar v-model="multipleValues" multiple locale="zh-CN" />'
      >
        <div class="space-y-3">
          <ECalendar v-model="multipleValues" multiple locale="zh-CN" class="rounded-md border" />
          <p v-if="multipleValues" class="text-sm text-muted-foreground">
            已选 {{ Array.isArray(multipleValues) ? multipleValues.length : 0 }} 个日期
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
  </ComponentDoc>
</template>
