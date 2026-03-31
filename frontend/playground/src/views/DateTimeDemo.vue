<script setup lang="ts">
import { ref } from 'vue'
import DemoBlock from '../components/DemoBlock.vue'
import ComponentDoc from '../components/ComponentDoc.vue'
import PropsTable from '../components/PropsTable.vue'
import EventsTable from '../components/EventsTable.vue'
import SlotsTable from '../components/SlotsTable.vue'

const date1 = ref('')
const date2 = ref('')
const time1 = ref('')
const time2 = ref('')
const dateDisabled = ref('2024-01-15')
const range = ref<string[]>([])
const monthValue = ref('')
const yearValue = ref('')

const tocItems = [
  { id: 'usage', label: '使用场景' },
  { id: 'date-basic', label: '日期选择' },
  { id: 'date-clearable', label: '可清除日期' },
  { id: 'date-disabled', label: '禁用日期' },
  { id: 'time-basic', label: '时间选择' },
  { id: 'time-step', label: '时间步长' },
  { id: 'date-range', label: '日期范围' },
  { id: 'month-year', label: '月份/年份' },
  { id: 'date-props', label: 'DatePicker Props' },
  { id: 'date-events', label: 'DatePicker Events' },
  { id: 'time-props', label: 'TimePicker Props' },
  { id: 'time-events', label: 'TimePicker Events' },
  { id: 'slots', label: 'Slots' },
]

const datePickerPropsData = [
  { name: 'modelValue', type: "string | Date | [string, string] | [Date, Date]", description: '绑定值，范围模式为数组' },
  { name: 'type', type: "'date' | 'daterange' | 'month' | 'year'", default: "'date'", description: '选择器类型' },
  { name: 'placeholder', type: 'string', description: '占位提示文字' },
  { name: 'startPlaceholder', type: 'string', description: '范围模式下开始日期占位文字' },
  { name: 'endPlaceholder', type: 'string', description: '范围模式下结束日期占位文字' },
  { name: 'rangeSeparator', type: 'string', description: '范围分隔符' },
  { name: 'format', type: 'string', description: '显示格式，如 "YYYY-MM-DD"' },
  { name: 'disabled', type: 'boolean', default: 'false', description: '是否禁用' },
  { name: 'clearable', type: 'boolean', default: 'false', description: '是否可清空' },
  { name: 'disabledDate', type: '(date: Date) => boolean', description: '自定义禁用日期判断函数' },
  { name: 'shortcuts', type: 'DatePickerShortcut[]', description: '快捷选项配置' },
  { name: 'class', type: 'string', description: '自定义 CSS 类名' },
]

const datePickerEventsData = [
  { name: 'update:modelValue', params: "(value: string | [string, string] | undefined)", description: '日期变化时触发（用于 v-model）' },
  { name: 'change', params: "(value: string | [string, string] | undefined)", description: '日期变化时触发' },
]

const timePickerPropsData = [
  { name: 'modelValue', type: 'string', description: '绑定值' },
  { name: 'placeholder', type: 'string', description: '占位提示文字' },
  { name: 'disabled', type: 'boolean', default: 'false', description: '是否禁用' },
  { name: 'format', type: 'string', description: '显示格式，如 "HH:mm:ss"' },
  { name: 'hourStep', type: 'number', description: '小时滚动步长' },
  { name: 'minuteStep', type: 'number', description: '分钟滚动步长' },
  { name: 'class', type: 'string', description: '自定义 CSS 类名' },
]

const timePickerEventsData = [
  { name: 'update:modelValue', params: '(value: string)', description: '时间变化时触发（用于 v-model）' },
  { name: 'change', params: '(value: string)', description: '时间变化时触发' },
]

const slotsData = [
  { name: 'default', description: '自定义触发器内容' },
]
</script>

<template>
  <ComponentDoc
    title="DatePicker & TimePicker 日期/时间选择器"
    description="日期和时间选择器组件，支持日期/月份/年份选择、日期范围、时间步长、禁用和可清除等特性。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">DatePicker 适用于需要选择日期的场景，如预约时间、报告日期筛选、生日录入等；TimePicker 适用于选择具体时间点的场景，如会议时间设置、闹钟配置等。日期范围选择适合筛选时间段的业务需求。</p>
    </section>

    <section id="date-basic">
      <DemoBlock
        title="日期选择器"
        description="基础日期选择，返回 YYYY-MM-DD 格式字符串"
        code='<EDatePicker v-model="date" placeholder="选择日期" />'
      >
        <div class="space-y-3 max-w-sm">
          <EDatePicker v-model="date1" placeholder="请选择日期" />
          <p class="text-sm text-muted-foreground">当前值：{{ date1 || '(未选择)' }}</p>
        </div>
      </DemoBlock>
    </section>

    <section id="date-clearable">
      <DemoBlock
        title="可清除的日期选择"
        description="设置 clearable 允许清除已选日期"
        code='<EDatePicker v-model="date" clearable placeholder="可清除的日期" />'
      >
        <div class="max-w-sm">
          <EDatePicker v-model="date2" :clearable="true" placeholder="选择后可清除" />
        </div>
      </DemoBlock>
    </section>

    <section id="date-disabled">
      <DemoBlock
        title="禁用日期选择"
        description="设置 disabled 禁用日期选择器"
        code='<EDatePicker v-model="date" :disabled="true" />'
      >
        <div class="max-w-sm">
          <EDatePicker v-model="dateDisabled" :disabled="true" />
        </div>
      </DemoBlock>
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

    <section id="date-range">
      <DemoBlock
        title="日期范围选择"
        description="设置 type='daterange' 选择起止日期"
        code='<EDatePicker v-model="range" type="daterange" start-placeholder="开始日期" end-placeholder="结束日期" />'
      >
        <div class="space-y-3 max-w-md">
          <EDatePicker v-model="range" type="daterange" start-placeholder="开始日期" end-placeholder="结束日期" />
          <p class="text-sm text-muted-foreground">当前值：{{ range && range.length ? range.join(' ~ ') : '(未选择)' }}</p>
        </div>
      </DemoBlock>
    </section>

    <section id="month-year">
      <DemoBlock
        title="月份/年份选择"
        description="设置 type='month' 或 type='year' 选择月份或年份"
        code='<EDatePicker v-model="month" type="month" placeholder="选择月份" />
<EDatePicker v-model="year" type="year" placeholder="选择年份" />'
      >
        <div class="flex gap-4 max-w-md">
          <div class="flex-1 space-y-2">
            <EDatePicker v-model="monthValue" type="month" placeholder="选择月份" />
            <p class="text-sm text-muted-foreground">月份：{{ monthValue || '(未选择)' }}</p>
          </div>
          <div class="flex-1 space-y-2">
            <EDatePicker v-model="yearValue" type="year" placeholder="选择年份" />
            <p class="text-sm text-muted-foreground">年份：{{ yearValue || '(未选择)' }}</p>
          </div>
        </div>
      </DemoBlock>
    </section>

    <section id="date-props">
      <h2 class="text-lg font-semibold mb-3">DatePicker Props</h2>
      <PropsTable :data="datePickerPropsData" />
    </section>

    <section id="date-events">
      <h2 class="text-lg font-semibold mb-3">DatePicker Events</h2>
      <EventsTable :data="datePickerEventsData" />
    </section>

    <section id="time-props">
      <h2 class="text-lg font-semibold mb-3">TimePicker Props</h2>
      <PropsTable :data="timePickerPropsData" />
    </section>

    <section id="time-events">
      <h2 class="text-lg font-semibold mb-3">TimePicker Events</h2>
      <EventsTable :data="timePickerEventsData" />
    </section>

    <section id="slots">
      <SlotsTable :data="slotsData" />
    </section>
  </ComponentDoc>
</template>
