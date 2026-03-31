<script setup lang="ts">
import { ref } from 'vue'
import { Bold, Italic, Underline } from 'lucide-vue-next'
import DemoBlock from '../components/DemoBlock.vue'
import ComponentDoc from '../components/ComponentDoc.vue'
import PropsTable from '../components/PropsTable.vue'
import EventsTable from '../components/EventsTable.vue'
import SlotsTable from '../components/SlotsTable.vue'

const boldOn = ref(false)
const italicOn = ref(false)
const underlineOn = ref(false)
const outlineOn = ref(false)
const disabledOn = ref(false)

const tocItems = [
  { id: 'usage', label: '使用场景' },
  { id: 'basic', label: '基础用法' },
  { id: 'outline', label: '描边变体' },
  { id: 'sizes', label: '尺寸' },
  { id: 'disabled', label: '禁用状态' },
  { id: 'props', label: 'Props' },
  { id: 'events', label: 'Events' },
  { id: 'slots', label: 'Slots' },
]

const propsData = [
  { name: 'modelValue', type: 'boolean', default: 'false', description: '切换状态（支持 v-model）' },
  { name: 'variant', type: "'default' | 'outline'", default: "'default'", description: '视觉变体' },
  { name: 'size', type: "'default' | 'sm' | 'lg'", default: "'default'", description: '按钮尺寸' },
  { name: 'disabled', type: 'boolean', default: 'false', description: '是否禁用' },
  { name: 'class', type: 'string', description: '自定义 CSS 类名' },
]

const eventsData = [
  { name: 'update:modelValue', params: '(value: boolean)', description: '切换状态变化时触发' },
]

const slotsData = [
  { name: 'default', description: '切换按钮内容（图标、文字等）' },
]
</script>

<template>
  <ComponentDoc
    title="Toggle 切换按钮"
    description="用于在「开」和「关」两种状态之间切换的按钮，常用于工具栏中的格式化选项。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">适用于需要在两个状态之间快速切换的场景，如富文本编辑器的加粗/斜体/下划线工具栏、视图模式切换、功能开关等。</p>
    </section>

    <section id="basic">
      <DemoBlock
        title="基础用法"
        description="默认变体的切换按钮，点击后进入激活（on）状态"
        code='<EToggle v-model="boldOn">
  <Bold class="size-4" />
</EToggle>
<EToggle v-model="italicOn">
  <Italic class="size-4" />
</EToggle>
<EToggle v-model="underlineOn">
  <Underline class="size-4" />
</EToggle>'
      >
        <div class="flex items-center gap-2">
          <EToggle v-model="boldOn">
            <Bold class="size-4" />
          </EToggle>
          <EToggle v-model="italicOn">
            <Italic class="size-4" />
          </EToggle>
          <EToggle v-model="underlineOn">
            <Underline class="size-4" />
          </EToggle>
          <span class="ml-4 text-sm text-muted-foreground">
            当前状态：B={{ boldOn }} / I={{ italicOn }} / U={{ underlineOn }}
          </span>
        </div>
      </DemoBlock>
    </section>

    <section id="outline">
      <DemoBlock
        title="描边变体"
        description="outline 变体带有边框，视觉上更明显"
        code='<EToggle v-model="outlineOn" variant="outline">
  <Bold class="size-4" />
</EToggle>'
      >
        <div class="flex items-center gap-2">
          <EToggle v-model="outlineOn" variant="outline">
            <Bold class="size-4" />
          </EToggle>
          <EToggle variant="outline">
            <Italic class="size-4" />
          </EToggle>
          <EToggle variant="outline">
            <Underline class="size-4" />
          </EToggle>
        </div>
      </DemoBlock>
    </section>

    <section id="sizes">
      <DemoBlock
        title="尺寸"
        description="3 种尺寸：sm、default、lg"
        code='<EToggle size="sm"><Bold class="size-4" /></EToggle>
<EToggle size="default"><Bold class="size-4" /></EToggle>
<EToggle size="lg"><Bold class="size-4" /></EToggle>'
      >
        <div class="flex items-center gap-3">
          <EToggle size="sm"><Bold class="size-4" /></EToggle>
          <EToggle size="default"><Bold class="size-4" /></EToggle>
          <EToggle size="lg"><Bold class="size-4" /></EToggle>
        </div>
      </DemoBlock>
    </section>

    <section id="disabled">
      <DemoBlock
        title="禁用状态"
        description="禁用后不响应任何交互"
        code='<EToggle :disabled="true"><Bold class="size-4" /></EToggle>'
      >
        <div class="flex items-center gap-3">
          <EToggle v-model="disabledOn" disabled>
            <Bold class="size-4" />
          </EToggle>
          <EToggle disabled variant="outline">
            <Italic class="size-4" />
          </EToggle>
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
