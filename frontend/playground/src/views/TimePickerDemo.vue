<script setup lang="ts">
import { ref } from 'vue'
import DemoBlock from '../components/DemoBlock.vue'
import ComponentDoc from '../components/ComponentDoc.vue'
import PropsTable from '../components/PropsTable.vue'
import EventsTable from '../components/EventsTable.vue'

const time1 = ref('')
const time2 = ref('')

const tocItems = [
  { id: 'usage', label: '使用场景' },
  { id: 'time-basic', label: '时间选择' },
  { id: 'time-step', label: '时间步长' },
  { id: 'props', label: 'Props' },
  { id: 'events', label: 'Events' },
]

const propsData = [
  { name: 'modelValue', type: 'string', description: '绑定值' },
  { name: 'placeholder', type: 'string', description: '占位提示文字' },
  { name: 'disabled', type: 'boolean', default: 'false', description: '是否禁用' },
  { name: 'format', type: 'string', description: '显示格式，如 "HH:mm:ss"' },
  { name: 'hourStep', type: 'number', description: '小时滚动步长' },
  { name: 'minuteStep', type: 'number', description: '分钟滚动步长' },
  { name: 'class', type: 'string', description: '自定义 CSS 类名' },
]

const eventsData = [
  { name: 'update:modelValue', params: '(value: string)', description: '时间变化时触发（用于 v-model）' },
  { name: 'change', params: '(value: string)', description: '时间变化时触发' },
]
</script>

<template>
  <ComponentDoc
    title="TimePicker 时间选择器"
    description="时间选择器组件，适用于选择具体时间点的场景，如会议时间设置、闹钟配置等。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">TimePicker 适用于选择具体时间点的场景，如会议时间设置、闹钟配置等。支持自定义时间步长和显示格式。</p>
    </section>

    <section id="time-basic">
      <DemoBlock
        title="时间选择器"
        description="基础时间选择，返回 HH:mm:ss 格式字符串"
        code='<ETimePicker v-model="time" placeholder="选择时间" />'
      >
        <div class="space-y-3 max-w-sm">
          <ETimePicker v-model="time1" placeholder="请选择时间" />
          <p class="text-sm text-muted-foreground">当前值：{{ time1 || '(未选择)' }}</p>
        </div>
      </DemoBlock>
    </section>

    <section id="time-step">
      <DemoBlock
        title="时间步长设置"
        description="通过 hourStep / minuteStep 设置小时和分钟步长"
        code='<ETimePicker v-model="time" :hourStep="1" :minuteStep="15" />'
      >
        <div class="max-w-sm">
          <ETimePicker v-model="time2" :minuteStep="15" placeholder="分钟步长 15" />
        </div>
      </DemoBlock>
    </section>

    <section id="props">
      <h2 class="text-lg font-semibold mb-3">TimePicker Props</h2>
      <PropsTable :data="propsData" />
    </section>

    <section id="events">
      <h2 class="text-lg font-semibold mb-3">TimePicker Events</h2>
      <EventsTable :data="eventsData" />
    </section>
  </ComponentDoc>
</template>
