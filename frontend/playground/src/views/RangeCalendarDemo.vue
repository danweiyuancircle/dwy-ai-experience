<script setup lang="ts">
import { ref } from 'vue'
import DemoBlock from '../components/DemoBlock.vue'
import ComponentDoc from '../components/ComponentDoc.vue'
import PropsTable from '../components/PropsTable.vue'
import EventsTable from '../components/EventsTable.vue'

const rangeValue = ref()

const tocItems = [
  { id: 'usage', label: '使用场景' },
  { id: 'basic', label: '基础范围选择' },
  { id: 'props', label: 'Props' },
  { id: 'events', label: 'Events' },
]

const propsData = [
  { name: 'modelValue', type: '{ start: DateValue; end: DateValue }', description: '选中的日期范围，支持 v-model' },
  { name: 'defaultValue', type: '{ start: DateValue; end: DateValue }', description: '默认选中的日期范围' },
  { name: 'disabled', type: 'boolean', default: 'false', description: '是否禁用日历' },
  { name: 'readonly', type: 'boolean', default: 'false', description: '是否只读' },
  { name: 'locale', type: 'string', description: "区域设置，如 'zh-CN'、'en-US'" },
  { name: 'minValue', type: 'DateValue', description: '可选日期范围的最小值' },
  { name: 'maxValue', type: 'DateValue', description: '可选日期范围的最大值' },
  { name: 'class', type: 'string', description: '自定义 CSS 类名' },
]

const eventsData = [
  { name: 'update:modelValue', params: '(value: { start: DateValue; end: DateValue } | null)', description: '选中日期范围变化时触发' },
]
</script>

<template>
  <ComponentDoc
    title="RangeCalendar 范围日历"
    description="日期范围选择日历面板，点击选择起始日期和结束日期，适用于预订、请假、统计等需要选择日期区间的场景。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">适用于需要选择日期区间的场景，如酒店预订选择入住/离店日期、请假申请选择起止日期、数据报表选择时间范围等。用户依次点击起始日期和结束日期完成范围选择。</p>
    </section>

    <section id="basic">
      <DemoBlock
        title="基础范围选择"
        description="点击第一个日期设为起始日期，点击第二个日期设为结束日期"
        code='<ERangeCalendar v-model="rangeValue" locale="zh-CN" />'
      >
        <div class="space-y-3">
          <ERangeCalendar v-model="rangeValue" locale="zh-CN" class="rounded-md border" />
          <p v-if="rangeValue?.start && rangeValue?.end" class="text-sm text-muted-foreground">
            选中范围:
            <code class="bg-muted px-1.5 py-0.5 rounded text-xs font-mono">{{ rangeValue.start }}</code>
            至
            <code class="bg-muted px-1.5 py-0.5 rounded text-xs font-mono">{{ rangeValue.end }}</code>
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
