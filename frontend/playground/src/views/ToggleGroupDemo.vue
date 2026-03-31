<script setup lang="ts">
import { ref } from 'vue'
import { AlignLeft, AlignCenter, AlignRight, Bold, Italic, Underline } from 'lucide-vue-next'
import DemoBlock from '../components/DemoBlock.vue'
import ComponentDoc from '../components/ComponentDoc.vue'
import PropsTable from '../components/PropsTable.vue'
import EventsTable from '../components/EventsTable.vue'
import SlotsTable from '../components/SlotsTable.vue'

const singleValue = ref('center')
const multipleValue = ref<string[]>(['bold'])

const tocItems = [
  { id: 'usage', label: '使用场景' },
  { id: 'single', label: '单选模式' },
  { id: 'multiple', label: '多选模式' },
  { id: 'variants', label: '变体与尺寸' },
  { id: 'disabled', label: '禁用状态' },
  { id: 'props', label: 'Props' },
  { id: 'events', label: 'Events' },
  { id: 'slots', label: 'Slots' },
]

const propsData = [
  { name: 'modelValue', type: "string | string[]", default: '—', description: '当前选中值（支持 v-model）' },
  { name: 'type', type: "'single' | 'multiple'", default: "'single'", description: '选择模式：单选或多选' },
  { name: 'variant', type: "'default' | 'outline'", default: "'default'", description: '视觉变体，传递给子项' },
  { name: 'size', type: "'default' | 'sm' | 'lg'", default: "'default'", description: '尺寸，传递给子项' },
  { name: 'disabled', type: 'boolean', default: 'false', description: '是否禁用整组' },
  { name: 'class', type: 'string', description: '自定义 CSS 类名' },
]

const eventsData = [
  { name: 'update:modelValue', params: '(value: string | string[])', description: '选中值变化时触发' },
]

const slotsData = [
  { name: 'default', description: '放置 EToggle 子项' },
]
</script>

<template>
  <ComponentDoc
    title="ToggleGroup 切换按钮组"
    description="将多个 Toggle 组合为一组，支持单选和多选模式，常用于工具栏选项组。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">适用于一组互斥或可多选的切换选项，如文本对齐方式（单选）、文本格式化选项（多选）等工具栏场景。</p>
    </section>

    <section id="single">
      <DemoBlock
        title="单选模式"
        description="type='single' 时，同一时间只能选中一个选项"
        code='<EToggleGroup v-model="singleValue" type="single">
  <EToggle value="left"><AlignLeft class="size-4" /></EToggle>
  <EToggle value="center"><AlignCenter class="size-4" /></EToggle>
  <EToggle value="right"><AlignRight class="size-4" /></EToggle>
</EToggleGroup>'
      >
        <div class="flex items-center gap-4">
          <EToggleGroup v-model="singleValue" type="single">
            <EToggle value="left"><AlignLeft class="size-4" /></EToggle>
            <EToggle value="center"><AlignCenter class="size-4" /></EToggle>
            <EToggle value="right"><AlignRight class="size-4" /></EToggle>
          </EToggleGroup>
          <span class="text-sm text-muted-foreground">当前选中：{{ singleValue }}</span>
        </div>
      </DemoBlock>
    </section>

    <section id="multiple">
      <DemoBlock
        title="多选模式"
        description="type='multiple' 时，可以同时选中多个选项"
        code='<EToggleGroup v-model="multipleValue" type="multiple">
  <EToggle value="bold"><Bold class="size-4" /></EToggle>
  <EToggle value="italic"><Italic class="size-4" /></EToggle>
  <EToggle value="underline"><Underline class="size-4" /></EToggle>
</EToggleGroup>'
      >
        <div class="flex items-center gap-4">
          <EToggleGroup v-model="multipleValue" type="multiple">
            <EToggle value="bold"><Bold class="size-4" /></EToggle>
            <EToggle value="italic"><Italic class="size-4" /></EToggle>
            <EToggle value="underline"><Underline class="size-4" /></EToggle>
          </EToggleGroup>
          <span class="text-sm text-muted-foreground">当前选中：{{ multipleValue.join(', ') || '无' }}</span>
        </div>
      </DemoBlock>
    </section>

    <section id="variants">
      <DemoBlock
        title="变体与尺寸"
        description="outline 变体 + 不同尺寸"
        code='<EToggleGroup type="single" variant="outline" size="sm">
  <EToggle value="left"><AlignLeft class="size-4" /></EToggle>
  <EToggle value="center"><AlignCenter class="size-4" /></EToggle>
  <EToggle value="right"><AlignRight class="size-4" /></EToggle>
</EToggleGroup>'
      >
        <div class="space-y-4">
          <div class="flex items-center gap-3">
            <span class="text-sm w-8">sm</span>
            <EToggleGroup type="single" variant="outline" size="sm">
              <EToggle value="left"><AlignLeft class="size-4" /></EToggle>
              <EToggle value="center"><AlignCenter class="size-4" /></EToggle>
              <EToggle value="right"><AlignRight class="size-4" /></EToggle>
            </EToggleGroup>
          </div>
          <div class="flex items-center gap-3">
            <span class="text-sm w-8">md</span>
            <EToggleGroup type="single" variant="outline">
              <EToggle value="left"><AlignLeft class="size-4" /></EToggle>
              <EToggle value="center"><AlignCenter class="size-4" /></EToggle>
              <EToggle value="right"><AlignRight class="size-4" /></EToggle>
            </EToggleGroup>
          </div>
          <div class="flex items-center gap-3">
            <span class="text-sm w-8">lg</span>
            <EToggleGroup type="single" variant="outline" size="lg">
              <EToggle value="left"><AlignLeft class="size-4" /></EToggle>
              <EToggle value="center"><AlignCenter class="size-4" /></EToggle>
              <EToggle value="right"><AlignRight class="size-4" /></EToggle>
            </EToggleGroup>
          </div>
        </div>
      </DemoBlock>
    </section>

    <section id="disabled">
      <DemoBlock
        title="禁用状态"
        description="整组禁用后所有子项不响应交互"
        code='<EToggleGroup type="single" disabled>
  <EToggle value="left"><AlignLeft class="size-4" /></EToggle>
  <EToggle value="center"><AlignCenter class="size-4" /></EToggle>
  <EToggle value="right"><AlignRight class="size-4" /></EToggle>
</EToggleGroup>'
      >
        <EToggleGroup type="single" disabled>
          <EToggle value="left"><AlignLeft class="size-4" /></EToggle>
          <EToggle value="center"><AlignCenter class="size-4" /></EToggle>
          <EToggle value="right"><AlignRight class="size-4" /></EToggle>
        </EToggleGroup>
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
