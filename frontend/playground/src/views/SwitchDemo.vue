<script setup lang="ts">
import { ref } from 'vue'
import DemoBlock from '../components/DemoBlock.vue'
import ComponentDoc from '../components/ComponentDoc.vue'
import PropsTable from '../components/PropsTable.vue'
import EventsTable from '../components/EventsTable.vue'
import SlotsTable from '../components/SlotsTable.vue'

const basic = ref(false)
const withLabel = ref(true)
const disabled = ref(false)
const sizeSm = ref(true)
const sizeLg = ref(false)

const tocItems = [
  { id: 'usage', label: '使用场景' },
  { id: 'basic', label: '基础开关' },
  { id: 'label', label: '带标签' },
  { id: 'disabled', label: '禁用状态' },
  { id: 'sizes', label: '尺寸变体' },
  { id: 'props', label: 'Props' },
  { id: 'events', label: 'Events' },
  { id: 'slots', label: 'Slots' },
]

const propsData = [
  { name: 'modelValue', type: 'boolean', description: '绑定值' },
  { name: 'label', type: 'string', description: '开关旁的文本标签' },
  { name: 'disabled', type: 'boolean', default: 'false', description: '是否禁用' },
  { name: 'size', type: "'sm' | 'default' | 'lg'", default: "'default'", description: '开关尺寸' },
  { name: 'class', type: 'string', description: '自定义 CSS 类名' },
]

const eventsData = [
  { name: 'update:modelValue', params: '(value: boolean)', description: '开关状态变化时触发（用于 v-model）' },
  { name: 'change', params: '(value: boolean)', description: '开关状态变化时触发' },
]

const slotsData = [
  { name: 'default', description: '自定义标签内容（替代 label prop）' },
]
</script>

<template>
  <ComponentDoc
    title="Switch 开关"
    description="开/关切换组件，支持标签文本、禁用和尺寸变体。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">适用于需要在两种状态间即时切换的场景，如开启/关闭通知推送、启用/禁用暗色模式、功能开关配置等。与 Checkbox 相比，Switch 更强调状态的即时生效，通常不需要额外的提交操作。</p>
    </section>

    <section id="basic">
      <DemoBlock
        title="基础开关"
        description="最简单的开关控件"
        code='<ESwitch v-model="value" />'
      >
        <div class="flex items-center gap-4">
          <ESwitch v-model="basic" />
          <span class="text-sm text-muted-foreground">当前：{{ basic ? '开' : '关' }}</span>
        </div>
      </DemoBlock>
    </section>

    <section id="label">
      <DemoBlock
        title="带标签"
        description="设置 label 属性显示说明文字"
        code='<ESwitch v-model="value" label="接收通知" />'
      >
        <div class="space-y-3">
          <ESwitch v-model="withLabel" label="接收通知" />
          <ESwitch v-model="basic" label="暗色模式" />
        </div>
      </DemoBlock>
    </section>

    <section id="disabled">
      <DemoBlock
        title="禁用状态"
        description="disabled 禁用开关交互"
        code='<ESwitch :disabled="true" label="禁用（关闭）" />
<ESwitch :modelValue="true" :disabled="true" label="禁用（开启）" />'
      >
        <div class="space-y-3">
          <ESwitch v-model="disabled" :disabled="true" label="禁用（关闭）" />
          <ESwitch :modelValue="true" :disabled="true" label="禁用（开启）" />
        </div>
      </DemoBlock>
    </section>

    <section id="sizes">
      <DemoBlock
        title="尺寸变体"
        description="支持 sm / default / lg 三种尺寸"
        code='<ESwitch v-model="value" size="sm" label="小号 sm" />
<ESwitch v-model="value" label="默认尺寸" />
<ESwitch v-model="value" size="lg" label="大号 lg" />'
      >
        <div class="space-y-3">
          <ESwitch v-model="sizeSm" size="sm" label="小号 sm" />
          <ESwitch v-model="basic" label="默认尺寸 default" />
          <ESwitch v-model="sizeLg" size="lg" label="大号 lg" />
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
