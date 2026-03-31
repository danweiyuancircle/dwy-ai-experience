<script setup lang="ts">
import { ref } from 'vue'
import DemoBlock from '../components/DemoBlock.vue'
import ComponentDoc from '../components/ComponentDoc.vue'
import PropsTable from '../components/PropsTable.vue'
import EventsTable from '../components/EventsTable.vue'
import SlotsTable from '../components/SlotsTable.vue'

const basic = ref('')
const clearable = ref('可清除的文字')
const password = ref('')
const disabled = ref('禁用状态的输入框')
const readonly = ref('只读状态的值')
const sizeSmall = ref('')
const sizeLarge = ref('')
const maxLen = ref('')
const wordLimitVal = ref('')

const tocItems = [
  { id: 'usage', label: '使用场景' },
  { id: 'basic', label: '基础用法' },
  { id: 'clearable', label: '可清除' },
  { id: 'password', label: '密码输入' },
  { id: 'disabled-readonly', label: '禁用与只读' },
  { id: 'sizes', label: '尺寸变体' },
  { id: 'maxlength', label: '最大长度' },
  { id: 'word-limit', label: '字数统计' },
  { id: 'props', label: 'Props' },
  { id: 'events', label: 'Events' },
  { id: 'slots', label: 'Slots' },
]

const propsData = [
  { name: 'modelValue', type: 'string | number', description: '绑定值' },
  { name: 'type', type: 'string', default: "'text'", description: 'input 原生 type 属性' },
  { name: 'placeholder', type: 'string', description: '占位提示文字' },
  { name: 'size', type: "'sm' | 'default' | 'lg'", default: "'default'", description: '输入框尺寸' },
  { name: 'disabled', type: 'boolean', default: 'false', description: '是否禁用' },
  { name: 'readonly', type: 'boolean', default: 'false', description: '是否只读' },
  { name: 'clearable', type: 'boolean', default: 'false', description: '是否可清空' },
  { name: 'maxlength', type: 'number', description: '最大输入字符数' },
  { name: 'showPassword', type: 'boolean', default: 'false', description: '是否显示密码可见切换按钮' },
  { name: 'showWordLimit', type: 'boolean', default: 'false', description: '是否显示字数统计（需配合 maxlength）' },
  { name: 'class', type: 'string', description: '自定义 CSS 类名' },
]

const eventsData = [
  { name: 'update:modelValue', params: '(value: string)', description: '输入值变化时触发（用于 v-model）' },
  { name: 'change', params: '(value: string)', description: '值改变且失焦时触发' },
  { name: 'blur', params: '(event: FocusEvent)', description: '失去焦点时触发' },
  { name: 'focus', params: '(event: FocusEvent)', description: '获得焦点时触发' },
  { name: 'clear', params: '()', description: '点击清除按钮时触发' },
]

const slotsData = [
  { name: 'prefix', description: '输入框前置内容' },
  { name: 'suffix', description: '输入框后置内容' },
]
</script>

<template>
  <ComponentDoc
    title="Input 输入框"
    description="基础文本输入组件，支持清除、密码模式、尺寸变体等特性。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">适用于表单中需要用户输入文本的场景，如登录表单的用户名/密码输入、搜索框关键词输入、个人信息编辑等。根据业务需求选择合适的特性：密码字段启用 showPassword，搜索框启用 clearable，限制字数时配合 maxlength + showWordLimit。</p>
    </section>

    <section id="basic">
      <DemoBlock
        title="基础用法"
        description="最简单的输入框"
        code='<EInput v-model="value" placeholder="请输入内容" />'
      >
        <div class="space-y-3 max-w-sm">
          <EInput v-model="basic" placeholder="请输入内容" />
          <p class="text-sm text-muted-foreground">当前值：{{ basic || '(空)' }}</p>
        </div>
      </DemoBlock>
    </section>

    <section id="clearable">
      <DemoBlock
        title="可清除"
        description="设置 clearable 显示清除按钮"
        code='<EInput v-model="value" clearable placeholder="输入后可清除" />'
      >
        <div class="space-y-3 max-w-sm">
          <EInput v-model="clearable" clearable placeholder="输入后可清除" />
          <p class="text-sm text-muted-foreground">当前值：{{ clearable || '(已清除)' }}</p>
        </div>
      </DemoBlock>
    </section>

    <section id="password">
      <DemoBlock
        title="密码输入"
        description="设置 showPassword 启用密码可见切换"
        code='<EInput v-model="password" type="password" showPassword placeholder="输入密码" />'
      >
        <div class="max-w-sm">
          <EInput v-model="password" type="password" :showPassword="true" placeholder="输入密码" />
        </div>
      </DemoBlock>
    </section>

    <section id="disabled-readonly">
      <DemoBlock
        title="禁用与只读"
        description="disabled 完全禁用，readonly 仅限只读"
        code='<EInput :disabled="true" value="禁用状态" />
<EInput :readonly="true" value="只读状态" />'
      >
        <div class="space-y-3 max-w-sm">
          <EInput v-model="disabled" :disabled="true" placeholder="禁用状态" />
          <EInput v-model="readonly" :readonly="true" placeholder="只读状态" />
        </div>
      </DemoBlock>
    </section>

    <section id="sizes">
      <DemoBlock
        title="尺寸变体"
        description="支持 sm / default / lg 三种尺寸"
        code='<EInput size="sm" placeholder="小尺寸" />
<EInput size="default" placeholder="默认尺寸" />
<EInput size="lg" placeholder="大尺寸" />'
      >
        <div class="space-y-3 max-w-sm">
          <EInput v-model="sizeSmall" size="sm" placeholder="小尺寸 sm" />
          <EInput placeholder="默认尺寸 default" />
          <EInput v-model="sizeLarge" size="lg" placeholder="大尺寸 lg" />
        </div>
      </DemoBlock>
    </section>

    <section id="maxlength">
      <DemoBlock
        title="最大长度"
        description="通过 maxlength 限制输入字符数"
        code='<EInput v-model="value" :maxlength="20" placeholder="最多输入 20 个字符" />'
      >
        <div class="max-w-sm">
          <EInput v-model="maxLen" :maxlength="20" placeholder="最多输入 20 个字符" />
          <p class="text-sm text-muted-foreground mt-2">{{ maxLen.length }}/20</p>
        </div>
      </DemoBlock>
    </section>

    <section id="word-limit">
      <DemoBlock
        title="字数统计"
        description="设置 show-word-limit 配合 maxlength 显示字数统计"
        code='<EInput v-model="val" :maxlength="50" show-word-limit placeholder="最多50字" />'
      >
        <div class="max-w-sm">
          <EInput v-model="wordLimitVal" :maxlength="50" show-word-limit placeholder="最多50字" />
        </div>
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
