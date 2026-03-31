<script setup lang="ts">
import { ref } from 'vue'
import DemoBlock from '../components/DemoBlock.vue'
import ComponentDoc from '../components/ComponentDoc.vue'
import PropsTable from '../components/PropsTable.vue'
import EventsTable from '../components/EventsTable.vue'
import SlotsTable from '../components/SlotsTable.vue'

const basicValue = ref('')
const fourDigitValue = ref('')

function handleComplete(value: string) {
  // eslint-disable-next-line no-console
  console.log('OTP 输入完成:', value)
}

const tocItems = [
  { id: 'usage', label: '使用场景' },
  { id: 'basic', label: '基础用法' },
  { id: 'four-digit', label: '4 位验证码' },
  { id: 'disabled', label: '禁用状态' },
  { id: 'props', label: 'Props' },
  { id: 'events', label: 'Events' },
]

const propsData = [
  { name: 'modelValue / v-model', type: 'string', default: "''", description: '绑定值' },
  { name: 'length', type: 'number', default: '—', description: '验证码位数' },
  { name: 'disabled', type: 'boolean', default: 'false', description: '是否禁用' },
  { name: 'placeholder', type: 'string', default: '—', description: '占位字符' },
  { name: 'class', type: 'string', default: '—', description: '自定义 CSS 类名' },
]

const eventsData = [
  { name: 'update:modelValue', params: '(value: string)', description: 'v-model 绑定值变化时触发' },
  { name: 'complete', params: '(value: string)', description: '所有位数输入完成时触发' },
]

const slotsData = [
  { name: 'default', description: '无默认插槽' },
]
</script>

<template>
  <ComponentDoc
    title="InputOTP 验证码输入"
    description="一次性密码（OTP）输入组件，每位独立输入框，自动跳转焦点。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">适用于短信验证码、邮箱验证码、双因素认证等需要输入一次性密码的场景。每位数字独立输入框，输入后自动跳转到下一位，支持粘贴整串验证码。</p>
    </section>

    <section id="basic">
      <DemoBlock
        title="基础用法"
        description="默认 6 位验证码输入，输入完成后触发 complete 事件"
        code='<EInputOtp v-model="value" :length="6" @complete="handleComplete" />'
      >
        <div class="space-y-3">
          <EInputOtp v-model="basicValue" :length="6" @complete="handleComplete" />
          <p class="text-sm text-muted-foreground">当前值：{{ basicValue || '（空）' }}</p>
        </div>
      </DemoBlock>
    </section>

    <section id="four-digit">
      <DemoBlock
        title="4 位验证码"
        description="设置 length 为 4，适用于简短验证码"
        code='<EInputOtp v-model="value" :length="4" />'
      >
        <div class="space-y-3">
          <EInputOtp v-model="fourDigitValue" :length="4" />
          <p class="text-sm text-muted-foreground">当前值：{{ fourDigitValue || '（空）' }}</p>
        </div>
      </DemoBlock>
    </section>

    <section id="disabled">
      <DemoBlock
        title="禁用状态"
        description="设置 disabled 禁止输入"
        code='<EInputOtp :length="6" disabled />'
      >
        <EInputOtp :length="6" disabled />
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
