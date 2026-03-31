<script setup lang="ts">
import { ref } from 'vue'
import DemoBlock from '../components/DemoBlock.vue'
import ComponentDoc from '../components/ComponentDoc.vue'
import PropsTable from '../components/PropsTable.vue'
import EventsTable from '../components/EventsTable.vue'
import SlotsTable from '../components/SlotsTable.vue'

const rate1 = ref(3)
const rate2 = ref(3.5)
const rate3 = ref(4)
const rateDisabled = ref(3.5)

const labels = ['很差', '较差', '一般', '不错', '很好']

const tocItems = [
  { id: 'usage', label: '使用场景' },
  { id: 'basic', label: '基础评分' },
  { id: 'half', label: '半星评分' },
  { id: 'max', label: '自定义最大值' },
  { id: 'text', label: '文字说明' },
  { id: 'disabled', label: '禁用状态' },
  { id: 'props', label: 'Props' },
  { id: 'events', label: 'Events' },
  { id: 'slots', label: 'Slots' },
]

const propsData = [
  { name: 'modelValue', type: 'number', description: '绑定值（当前评分）' },
  { name: 'max', type: 'number', default: '5', description: '最大星数' },
  { name: 'disabled', type: 'boolean', default: 'false', description: '是否禁用（展示模式）' },
  { name: 'allowHalf', type: 'boolean', default: 'false', description: '是否允许半星选择' },
  { name: 'showText', type: 'boolean', default: 'false', description: '是否在右侧显示评分文字' },
  { name: 'class', type: 'string', description: '自定义 CSS 类名' },
]

const eventsData = [
  { name: 'update:modelValue', params: '(value: number)', description: '评分变化时触发（用于 v-model）' },
  { name: 'change', params: '(value: number)', description: '评分变化时触发' },
]

const slotsData = [
  { name: 'icon', description: '自定义星星图标' },
]
</script>

<template>
  <ComponentDoc
    title="Rate 评分"
    description="星级评分组件，支持半星、最大分值设置、禁用状态。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">适用于对事物进行评级或展示评级结果的场景，如商品评价、课程满意度调查、用户反馈收集等。设置 disabled 可用于纯展示已有评分，启用 allowHalf 可提供更精细的评分粒度。</p>
    </section>

    <section id="basic">
      <DemoBlock
        title="基础评分"
        description="点击或悬停设置评分"
        code='<ERate v-model="rate" />'
      >
        <div class="space-y-3">
          <ERate v-model="rate1" />
          <p class="text-sm text-muted-foreground">当前评分：{{ rate1 }} 分</p>
        </div>
      </DemoBlock>
    </section>

    <section id="half">
      <DemoBlock
        title="半星评分"
        description="设置 allowHalf 允许选择半星"
        code='<ERate v-model="rate" :allowHalf="true" />'
      >
        <div class="space-y-3">
          <ERate v-model="rate2" :allowHalf="true" />
          <p class="text-sm text-muted-foreground">当前评分：{{ rate2 }} 分（支持半星）</p>
        </div>
      </DemoBlock>
    </section>

    <section id="max">
      <DemoBlock
        title="自定义最大分值"
        description="通过 max 设置最大星数"
        code='<ERate v-model="rate" :max="10" />'
      >
        <div class="space-y-3">
          <ERate v-model="rate3" :max="10" />
          <p class="text-sm text-muted-foreground">当前评分：{{ rate3 }} / 10</p>
        </div>
      </DemoBlock>
    </section>

    <section id="text">
      <DemoBlock
        title="显示文字说明"
        description="设置 showText 在评分右侧显示说明文字"
        code='<ERate v-model="rate" :showText="true" />'
      >
        <div class="space-y-3">
          <div class="flex items-center gap-3">
            <ERate v-model="rate1" :showText="true" />
            <span class="text-sm text-muted-foreground">{{ labels[rate1 - 1] || '' }}</span>
          </div>
        </div>
      </DemoBlock>
    </section>

    <section id="disabled">
      <DemoBlock
        title="禁用状态"
        description="设置 disabled 禁用评分交互（展示模式）"
        code='<ERate v-model="rate" :disabled="true" />'
      >
        <div class="space-y-3">
          <ERate v-model="rateDisabled" :disabled="true" :allowHalf="true" />
          <p class="text-sm text-muted-foreground">展示模式，不可更改（{{ rateDisabled }} 分）</p>
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
