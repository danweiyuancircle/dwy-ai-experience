<script setup lang="ts">
import { ref } from 'vue'
import DemoBlock from '../components/DemoBlock.vue'
import ComponentDoc from '../components/ComponentDoc.vue'
import PropsTable from '../components/PropsTable.vue'
import EventsTable from '../components/EventsTable.vue'
import SlotsTable from '../components/SlotsTable.vue'

const basicValue = ref<string[]>([])
const maskedValue = ref<string[]>([])

function handleComplete(value: string[]) {
  // eslint-disable-next-line no-console
  console.log('PIN 输入完成:', value.join(''))
}

const tocItems = [
  { id: 'usage', label: '使用场景' },
  { id: 'basic', label: '基础用法' },
  { id: 'masked', label: '密码模式' },
  { id: 'disabled', label: '禁用状态' },
  { id: 'props', label: 'Props' },
  { id: 'events', label: 'Events' },
]

const propsData = [
  { name: 'modelValue / v-model', type: 'string[]', default: '[]', description: '绑定值，每位为数组中的一个元素' },
  { name: 'length', type: 'number', default: '—', description: '输入位数' },
  { name: 'disabled', type: 'boolean', default: 'false', description: '是否禁用' },
  { name: 'mask', type: 'boolean', default: 'false', description: '是否掩码显示（密码模式）' },
  { name: 'otp', type: 'boolean', default: 'false', description: '是否启用 OTP 自动填充（autocomplete="one-time-code"）' },
  { name: 'type', type: "'text' | 'number'", default: "'text'", description: '输入类型' },
  { name: 'class', type: 'string', default: '—', description: '自定义 CSS 类名' },
]

const eventsData = [
  { name: 'update:modelValue', params: '(value: string[])', description: 'v-model 绑定值变化时触发' },
  { name: 'complete', params: '(value: string[])', description: '所有位数输入完成时触发' },
]

const slotsData = [
  { name: 'default', description: '无默认插槽' },
]
</script>

<template>
  <ComponentDoc
    title="PinInput PIN 码输入"
    description="用于输入 PIN 码或密码，支持掩码模式，每位独立输入框。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">适用于 PIN 码、安全密码、支付密码等需要逐位输入的场景。与 InputOTP 类似但值为字符串数组，支持 mask 密码掩码模式和 otp 自动填充。</p>
    </section>

    <section id="basic">
      <DemoBlock
        title="基础用法"
        description="默认 4 位 PIN 码输入，输入完成后触发 complete 事件"
        code='<EPinInput v-model="value" :length="4" @complete="handleComplete" />'
      >
        <div class="space-y-3">
          <EPinInput v-model="basicValue" :length="4" @complete="handleComplete" />
          <p class="text-sm text-muted-foreground">当前值：{{ basicValue.length ? basicValue.join('') : '（空）' }}</p>
        </div>
      </DemoBlock>
    </section>

    <section id="masked">
      <DemoBlock
        title="密码模式"
        description="开启 mask 后输入内容以圆点掩码显示"
        code='<EPinInput v-model="value" :length="6" mask />'
      >
        <div class="space-y-3">
          <EPinInput v-model="maskedValue" :length="6" mask />
          <p class="text-sm text-muted-foreground">当前值：{{ maskedValue.length ? maskedValue.join('') : '（空）' }}</p>
        </div>
      </DemoBlock>
    </section>

    <section id="disabled">
      <DemoBlock
        title="禁用状态"
        description="设置 disabled 禁止输入"
        code='<EPinInput :length="4" disabled />'
      >
        <EPinInput :length="4" disabled />
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
