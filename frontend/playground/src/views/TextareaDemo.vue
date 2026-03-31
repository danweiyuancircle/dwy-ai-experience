<script setup lang="ts">
import { ref } from 'vue'
import DemoBlock from '../components/DemoBlock.vue'
import ComponentDoc from '../components/ComponentDoc.vue'
import PropsTable from '../components/PropsTable.vue'
import EventsTable from '../components/EventsTable.vue'
import SlotsTable from '../components/SlotsTable.vue'

const basicValue = ref('')
const autoResizeValue = ref('')
const limitValue = ref('')

const tocItems = [
  { id: 'usage', label: '使用场景' },
  { id: 'basic', label: '基础用法' },
  { id: 'auto-resize', label: '自适应高度' },
  { id: 'word-limit', label: '字数限制' },
  { id: 'disabled', label: '禁用与只读' },
  { id: 'props', label: 'Props' },
  { id: 'events', label: 'Events' },
  { id: 'slots', label: 'Slots' },
]

const propsData = [
  { name: 'modelValue / v-model', type: 'string', default: "''", description: '绑定值' },
  { name: 'placeholder', type: 'string', default: "—", description: '输入框占位文本' },
  { name: 'rows', type: 'number', default: '—', description: '输入框行数' },
  { name: 'disabled', type: 'boolean', default: 'false', description: '是否禁用' },
  { name: 'readonly', type: 'boolean', default: 'false', description: '是否只读' },
  { name: 'maxlength', type: 'number', default: '—', description: '最大输入长度' },
  { name: 'autoResize', type: 'boolean', default: 'false', description: '是否根据内容自动调整高度' },
  { name: 'showWordLimit', type: 'boolean', default: 'false', description: '设置 maxlength 后是否显示字数统计' },
  { name: 'minRows', type: 'number', default: '—', description: 'autoResize 启用时的最小行数' },
  { name: 'maxRows', type: 'number', default: '—', description: 'autoResize 启用时的最大行数（超出后出现滚动条）' },
  { name: 'class', type: 'string', default: '—', description: '自定义 CSS 类名' },
]

const eventsData = [
  { name: 'update:modelValue', params: '(value: string)', description: 'v-model 绑定值变化时触发' },
  { name: 'change', params: '(value: string)', description: '值改变时触发' },
  { name: 'blur', params: '(event: FocusEvent)', description: '失焦时触发' },
  { name: 'focus', params: '(event: FocusEvent)', description: '获焦时触发' },
]

const slotsData = [
  { name: 'default', description: '无默认插槽' },
]
</script>

<template>
  <ComponentDoc
    title="Textarea 文本域"
    description="用于多行文本输入，支持自适应高度、字数限制等功能。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">适用于评论、描述、备注等需要多行文本输入的场景。配合 maxlength 和 showWordLimit 可限制输入长度并给用户实时反馈，autoResize 则让输入框高度跟随内容自动增长。</p>
    </section>

    <section id="basic">
      <DemoBlock
        title="基础用法"
        description="通过 v-model 绑定文本值，设置 placeholder 和 rows"
        code='<ETextarea v-model="value" placeholder="请输入内容" :rows="3" />'
      >
        <div class="space-y-2 max-w-md">
          <ETextarea v-model="basicValue" placeholder="请输入内容" :rows="3" />
          <p class="text-sm text-muted-foreground">当前值：{{ basicValue || '（空）' }}</p>
        </div>
      </DemoBlock>
    </section>

    <section id="auto-resize">
      <DemoBlock
        title="自适应高度"
        description="开启 autoResize 后，输入框高度会随内容自动调整，可设置 minRows 和 maxRows 限制范围"
        code='<ETextarea v-model="value" autoResize :minRows="2" :maxRows="6" placeholder="输入多行内容试试" />'
      >
        <div class="max-w-md">
          <ETextarea v-model="autoResizeValue" auto-resize :min-rows="2" :max-rows="6" placeholder="输入多行内容，高度会自动调整" />
        </div>
      </DemoBlock>
    </section>

    <section id="word-limit">
      <DemoBlock
        title="字数限制"
        description="设置 maxlength 配合 showWordLimit 显示字数统计"
        code='<ETextarea v-model="value" :maxlength="100" showWordLimit placeholder="最多100个字符" />'
      >
        <div class="max-w-md">
          <ETextarea v-model="limitValue" :maxlength="100" show-word-limit placeholder="最多100个字符" :rows="3" />
        </div>
      </DemoBlock>
    </section>

    <section id="disabled">
      <DemoBlock
        title="禁用与只读"
        description="disabled 完全禁用输入，readonly 允许选中但不可编辑"
        code='<ETextarea disabled placeholder="禁用状态" />
<ETextarea readonly model-value="只读内容，可以选中复制但无法编辑" />'
      >
        <div class="space-y-3 max-w-md">
          <ETextarea disabled placeholder="禁用状态" :rows="2" />
          <ETextarea readonly model-value="只读内容，可以选中复制但无法编辑" :rows="2" />
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
