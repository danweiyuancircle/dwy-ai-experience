<script setup lang="ts">
import { ref } from 'vue'
import DemoBlock from '../components/DemoBlock.vue'
import ComponentDoc from '../components/ComponentDoc.vue'
import PropsTable from '../components/PropsTable.vue'
import EventsTable from '../components/EventsTable.vue'
import SlotsTable from '../components/SlotsTable.vue'

const basicColor = ref('#409eff')
const presetColor = ref('#67c23a')
const alphaColor = ref('rgba(64, 158, 255, 0.8)')

const presets = [
  '#ff4500',
  '#ff8c00',
  '#ffd700',
  '#90ee90',
  '#00ced1',
  '#409eff',
  '#c71585',
  '#7b68ee',
]

const tocItems = [
  { id: 'usage', label: '使用场景' },
  { id: 'basic', label: '基础用法' },
  { id: 'presets', label: '预设颜色' },
  { id: 'alpha', label: '透明度' },
  { id: 'disabled', label: '禁用状态' },
  { id: 'props', label: 'Props' },
  { id: 'events', label: 'Events' },
]

const propsData = [
  { name: 'modelValue / v-model', type: 'string', default: '—', description: '绑定的颜色值' },
  { name: 'presets', type: 'string[]', default: '—', description: '预设颜色列表' },
  { name: 'showAlpha', type: 'boolean', default: 'false', description: '是否支持透明度选择' },
  { name: 'disabled', type: 'boolean', default: 'false', description: '是否禁用' },
  { name: 'class', type: 'string', default: '—', description: '自定义 CSS 类名' },
]

const eventsData = [
  { name: 'update:modelValue', params: '(value: string)', description: 'v-model 绑定值变化时触发' },
  { name: 'change', params: '(value: string)', description: '颜色改变时触发' },
]

const slotsData = [
  { name: 'default', description: '无默认插槽' },
]
</script>

<template>
  <ComponentDoc
    title="ColorPicker 颜色选择器"
    description="用于颜色选取，支持预设色板和透明度调节。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">适用于主题配色、标签颜色、图表配色等需要用户选择颜色的场景。可提供预设色板快速选取，也支持自由选色和透明度调节。</p>
    </section>

    <section id="basic">
      <DemoBlock
        title="基础用法"
        description="通过 v-model 绑定颜色值"
        code='<EColorPicker v-model="color" />'
      >
        <div class="flex items-center gap-4">
          <EColorPicker v-model="basicColor" />
          <span class="text-sm text-muted-foreground">当前颜色：{{ basicColor }}</span>
        </div>
      </DemoBlock>
    </section>

    <section id="presets">
      <DemoBlock
        title="预设颜色"
        description="通过 presets 提供一组预定义颜色供快速选取"
        code="<EColorPicker v-model=&quot;color&quot; :presets=&quot;['#ff4500', '#ff8c00', '#ffd700', '#90ee90', '#00ced1', '#409eff']&quot; />"
      >
        <div class="flex items-center gap-4">
          <EColorPicker v-model="presetColor" :presets="presets" />
          <span class="text-sm text-muted-foreground">当前颜色：{{ presetColor }}</span>
        </div>
      </DemoBlock>
    </section>

    <section id="alpha">
      <DemoBlock
        title="透明度"
        description="开启 showAlpha 支持调节颜色透明度"
        code='<EColorPicker v-model="color" showAlpha />'
      >
        <div class="flex items-center gap-4">
          <EColorPicker v-model="alphaColor" show-alpha />
          <span class="text-sm text-muted-foreground">当前颜色：{{ alphaColor }}</span>
        </div>
      </DemoBlock>
    </section>

    <section id="disabled">
      <DemoBlock
        title="禁用状态"
        description="设置 disabled 禁止交互"
        code='<EColorPicker model-value="#409eff" disabled />'
      >
        <EColorPicker model-value="#409eff" disabled />
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
