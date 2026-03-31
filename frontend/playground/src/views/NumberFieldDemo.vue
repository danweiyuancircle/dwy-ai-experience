<script setup lang="ts">
import { ref } from 'vue'
import DemoBlock from '../components/DemoBlock.vue'
import ComponentDoc from '../components/ComponentDoc.vue'
import PropsTable from '../components/PropsTable.vue'
import EventsTable from '../components/EventsTable.vue'
import SlotsTable from '../components/SlotsTable.vue'

const basicValue = ref(0)
const rangeValue = ref(5)
const precisionValue = ref(1.0)
const rightValue = ref(0)

const tocItems = [
  { id: 'usage', label: '使用场景' },
  { id: 'basic', label: '基础用法' },
  { id: 'range', label: '范围与步长' },
  { id: 'precision', label: '精度控制' },
  { id: 'controls-right', label: '按钮位置' },
  { id: 'disabled', label: '禁用与只读' },
  { id: 'props', label: 'Props' },
  { id: 'events', label: 'Events' },
]

const propsData = [
  { name: 'modelValue / v-model', type: 'number', default: '—', description: '绑定值' },
  { name: 'min', type: 'number', default: '—', description: '允许的最小值' },
  { name: 'max', type: 'number', default: '—', description: '允许的最大值' },
  { name: 'step', type: 'number', default: '1', description: '每次增减的步长' },
  { name: 'disabled', type: 'boolean', default: 'false', description: '是否禁用' },
  { name: 'size', type: "'sm' | 'md' | 'lg'", default: "'md'", description: '输入框尺寸' },
  { name: 'precision', type: 'number', default: '—', description: '数值精度（小数位数）' },
  { name: 'controlsPosition', type: "'default' | 'right'", default: "'default'", description: '控制按钮位置' },
  { name: 'placeholder', type: 'string', default: '—', description: '输入框占位文本' },
  { name: 'readonly', type: 'boolean', default: 'false', description: '是否只读' },
  { name: 'class', type: 'string', default: '—', description: '自定义 CSS 类名' },
]

const eventsData = [
  { name: 'update:modelValue', params: '(value: number)', description: 'v-model 绑定值变化时触发' },
  { name: 'change', params: '(value: number)', description: '值改变时触发' },
]
</script>

<template>
  <ComponentDoc
    title="NumberField 数字输入框"
    description="用于数值输入，支持步进按钮、范围限制、精度控制。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">适用于数量、价格、年龄等需要精确数值输入的场景。通过 min/max 限制范围，step 控制步长，precision 控制小数位数。</p>
    </section>

    <section id="basic">
      <DemoBlock
        title="基础用法"
        description="通过 v-model 绑定数值，左右按钮可增减"
        code='<ENumberField v-model="value" placeholder="请输入数字" />'
      >
        <div class="space-y-2">
          <ENumberField v-model="basicValue" placeholder="请输入数字" />
          <p class="text-sm text-muted-foreground">当前值：{{ basicValue }}</p>
        </div>
      </DemoBlock>
    </section>

    <section id="range">
      <DemoBlock
        title="范围与步长"
        description="通过 min、max 限制范围，step 设置步长"
        code='<ENumberField v-model="value" :min="0" :max="10" :step="2" />'
      >
        <div class="space-y-2">
          <ENumberField v-model="rangeValue" :min="0" :max="10" :step="2" />
          <p class="text-sm text-muted-foreground">范围 0-10，步长 2，当前值：{{ rangeValue }}</p>
        </div>
      </DemoBlock>
    </section>

    <section id="precision">
      <DemoBlock
        title="精度控制"
        description="通过 precision 控制小数位数"
        code='<ENumberField v-model="value" :precision="2" :step="0.1" />'
      >
        <div class="space-y-2">
          <ENumberField v-model="precisionValue" :precision="2" :step="0.1" />
          <p class="text-sm text-muted-foreground">精度 2 位小数，当前值：{{ precisionValue }}</p>
        </div>
      </DemoBlock>
    </section>

    <section id="controls-right">
      <DemoBlock
        title="按钮位置"
        description="设置 controlsPosition 为 right，将增减按钮放在右侧"
        code='<ENumberField v-model="value" controlsPosition="right" />'
      >
        <ENumberField v-model="rightValue" controls-position="right" />
      </DemoBlock>
    </section>

    <section id="disabled">
      <DemoBlock
        title="禁用与只读"
        description="disabled 禁止交互，readonly 仅可查看"
        code='<ENumberField :model-value="10" disabled />
<ENumberField :model-value="20" readonly />'
      >
        <div class="flex flex-wrap gap-3">
          <ENumberField :model-value="10" disabled />
          <ENumberField :model-value="20" readonly />
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
