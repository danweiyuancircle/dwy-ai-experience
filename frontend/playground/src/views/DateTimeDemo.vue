<script setup lang="ts">
import { ref } from 'vue'
import DemoBlock from '../components/DemoBlock.vue'

const date1 = ref('')
const date2 = ref('')
const time1 = ref('')
const time2 = ref('')
const dateDisabled = ref('2024-01-15')
</script>

<template>
  <div class="max-w-3xl">
    <h1 class="text-2xl font-bold mb-2">DatePicker & TimePicker</h1>
    <p class="text-muted-foreground mb-6">日期和时间选择器组件，支持格式化、禁用、可清除等特性。</p>

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

    <DemoBlock
      title="可清除的日期选择"
      description="设置 clearable 允许清除已选日期"
      code='<EDatePicker v-model="date" clearable placeholder="可清除的日期" />'
    >
      <div class="max-w-sm">
        <EDatePicker v-model="date2" :clearable="true" placeholder="选择后可清除" />
      </div>
    </DemoBlock>

    <DemoBlock
      title="禁用日期选择"
      description="设置 disabled 禁用日期选择器"
      code='<EDatePicker v-model="date" :disabled="true" />'
    >
      <div class="max-w-sm">
        <EDatePicker v-model="dateDisabled" :disabled="true" />
      </div>
    </DemoBlock>

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

    <DemoBlock
      title="时间步长设置"
      description="通过 hourStep / minuteStep 设置小时和分钟步长"
      code='<ETimePicker v-model="time" :hourStep="1" :minuteStep="15" />'
    >
      <div class="max-w-sm">
        <ETimePicker v-model="time2" :minuteStep="15" placeholder="分钟步长 15" />
      </div>
    </DemoBlock>
  </div>
</template>
