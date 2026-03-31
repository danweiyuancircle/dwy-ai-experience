<script setup lang="ts">
import { ref } from 'vue'
import DemoBlock from '../components/DemoBlock.vue'
import ComponentDoc from '../components/ComponentDoc.vue'
import PropsTable from '../components/PropsTable.vue'
import EventsTable from '../components/EventsTable.vue'
import SlotsTable from '../components/SlotsTable.vue'

const single = ref([50])
const range = ref([20, 80])
const stepped = ref([30])
const disabled = ref([60])

const tocItems = [
  { id: 'usage', label: '使用场景' },
  { id: 'basic', label: '基础滑块' },
  { id: 'range', label: '范围选择' },
  { id: 'step', label: '步长设置' },
  { id: 'disabled', label: '禁用状态' },
  { id: 'example', label: '实际场景' },
  { id: 'props', label: 'Props' },
  { id: 'events', label: 'Events' },
  { id: 'slots', label: 'Slots' },
]

const propsData = [
  { name: 'modelValue', type: 'number[]', description: '绑定值，单滑块为单元素数组，范围为双元素数组' },
  { name: 'min', type: 'number', default: '0', description: '最小值' },
  { name: 'max', type: 'number', default: '100', description: '最大值' },
  { name: 'step', type: 'number', default: '1', description: '步长' },
  { name: 'disabled', type: 'boolean', default: 'false', description: '是否禁用' },
  { name: 'orientation', type: "'horizontal' | 'vertical'", default: "'horizontal'", description: '滑块方向' },
  { name: 'class', type: 'string', description: '自定义 CSS 类名' },
]

const eventsData = [
  { name: 'update:modelValue', params: '(value: number[])', description: '值变化时触发（用于 v-model）' },
]

const slotsData = [
  { name: 'thumb', description: '自定义滑块拖动手柄' },
]
</script>

<template>
  <ComponentDoc
    title="Slider 滑块"
    description="滑动输入组件，支持单滑块、范围选择、步长设置和禁用状态。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">适用于在连续或离散的数值范围内进行选择的场景，如音量/亮度调节、价格区间筛选、进度设置等。范围模式适合价格区间、时间范围等需要设置上下界的场景。</p>
    </section>

    <section id="basic">
      <DemoBlock
        title="基础滑块"
        description="单滑块，拖动选择值"
        code='<ESlider v-model="value" :min="0" :max="100" />'
      >
        <div class="space-y-4">
          <ESlider v-model="single" :min="0" :max="100" />
          <p class="text-sm text-muted-foreground">当前值：{{ single[0] }}</p>
        </div>
      </DemoBlock>
    </section>

    <section id="range">
      <DemoBlock
        title="范围选择"
        description="通过双值数组实现范围选择滑块"
        code='<ESlider v-model="range" :min="0" :max="100" />'
      >
        <div class="space-y-4">
          <ESlider v-model="range" :min="0" :max="100" />
          <p class="text-sm text-muted-foreground">范围：{{ range[0] }} — {{ range[1] }}</p>
        </div>
      </DemoBlock>
    </section>

    <section id="step">
      <DemoBlock
        title="步长设置"
        description="通过 step 设置每次移动的步长"
        code='<ESlider v-model="value" :min="0" :max="100" :step="10" />'
      >
        <div class="space-y-4">
          <ESlider v-model="stepped" :min="0" :max="100" :step="10" />
          <p class="text-sm text-muted-foreground">当前值：{{ stepped[0] }}（步长 10）</p>
        </div>
      </DemoBlock>
    </section>

    <section id="disabled">
      <DemoBlock
        title="禁用状态"
        description="设置 disabled 禁用拖动"
        code='<ESlider v-model="value" :disabled="true" />'
      >
        <ESlider v-model="disabled" :disabled="true" />
      </DemoBlock>
    </section>

    <section id="example">
      <DemoBlock title="音量控制示例" description="Slider 在实际场景中的应用">
        <div class="space-y-4">
          <div class="flex items-center gap-3">
            <span class="text-sm text-muted-foreground w-12">音量</span>
            <ESlider v-model="single" :min="0" :max="100" class="flex-1" />
            <span class="text-sm font-medium w-8">{{ single[0] }}</span>
          </div>
          <div class="flex items-center gap-3">
            <span class="text-sm text-muted-foreground w-12">亮度</span>
            <ESlider v-model="stepped" :min="0" :max="100" :step="5" class="flex-1" />
            <span class="text-sm font-medium w-8">{{ stepped[0] }}%</span>
          </div>
          <div class="flex items-center gap-3">
            <span class="text-sm text-muted-foreground w-12">价格</span>
            <ESlider v-model="range" :min="0" :max="1000" :step="50" class="flex-1" />
            <span class="text-sm font-medium w-24">{{ range[0] }}-{{ range[1] }}</span>
          </div>
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
