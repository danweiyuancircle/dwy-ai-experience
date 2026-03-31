<script setup lang="ts">
import { ChevronLeft, ChevronRight, Plus, Minus, Copy, Clipboard, Download } from 'lucide-vue-next'
import DemoBlock from '../components/DemoBlock.vue'
import ComponentDoc from '../components/ComponentDoc.vue'
import PropsTable from '../components/PropsTable.vue'
import SlotsTable from '../components/SlotsTable.vue'

const tocItems = [
  { id: 'usage', label: '使用场景' },
  { id: 'horizontal', label: '水平排列' },
  { id: 'vertical', label: '垂直排列' },
  { id: 'variants', label: '不同变体组合' },
  { id: 'props', label: 'Props' },
  { id: 'slots', label: 'Slots' },
]

const propsData = [
  { name: 'orientation', type: "'horizontal' | 'vertical'", default: "'horizontal'", description: '排列方向' },
  { name: 'class', type: 'string', description: '自定义 CSS 类名' },
]

const slotsData = [
  { name: 'default', description: '放置 EButton 子项，相邻按钮边框自动合并' },
]
</script>

<template>
  <ComponentDoc
    title="ButtonGroup 按钮组"
    description="将多个按钮组合在一起，自动合并相邻按钮的边框和圆角，支持水平和垂直排列。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">适用于一组关联操作需要紧凑排列的场景，如分页器的上一页/下一页、工具栏的操作按钮组、数值增减控件等。</p>
    </section>

    <section id="horizontal">
      <DemoBlock
        title="水平排列"
        description="默认水平方向，相邻按钮左右边框合并"
        code='<EButtonGroup>
  <EButton variant="outline"><ChevronLeft class="size-4" /></EButton>
  <EButton variant="outline">第 1 页</EButton>
  <EButton variant="outline"><ChevronRight class="size-4" /></EButton>
</EButtonGroup>'
      >
        <div class="space-y-4">
          <EButtonGroup>
            <EButton variant="outline"><ChevronLeft class="size-4" /></EButton>
            <EButton variant="outline">第 1 页</EButton>
            <EButton variant="outline"><ChevronRight class="size-4" /></EButton>
          </EButtonGroup>

          <EButtonGroup>
            <EButton variant="outline"><Minus class="size-4" /></EButton>
            <EButton variant="outline"><Plus class="size-4" /></EButton>
          </EButtonGroup>

          <EButtonGroup>
            <EButton variant="outline"><Copy class="size-4" /> 复制</EButton>
            <EButton variant="outline"><Clipboard class="size-4" /> 粘贴</EButton>
            <EButton variant="outline"><Download class="size-4" /> 下载</EButton>
          </EButtonGroup>
        </div>
      </DemoBlock>
    </section>

    <section id="vertical">
      <DemoBlock
        title="垂直排列"
        description="orientation='vertical' 时上下排列，相邻按钮上下边框合并"
        code='<EButtonGroup orientation="vertical">
  <EButton variant="outline">选项一</EButton>
  <EButton variant="outline">选项二</EButton>
  <EButton variant="outline">选项三</EButton>
</EButtonGroup>'
      >
        <EButtonGroup orientation="vertical">
          <EButton variant="outline">选项一</EButton>
          <EButton variant="outline">选项二</EButton>
          <EButton variant="outline">选项三</EButton>
        </EButtonGroup>
      </DemoBlock>
    </section>

    <section id="variants">
      <DemoBlock
        title="不同变体组合"
        description="按钮组内的按钮可以使用不同变体"
      >
        <div class="space-y-4">
          <EButtonGroup>
            <EButton>确认</EButton>
            <EButton variant="outline">取消</EButton>
          </EButtonGroup>

          <EButtonGroup>
            <EButton variant="secondary">上一步</EButton>
            <EButton>下一步</EButton>
          </EButtonGroup>
        </div>
      </DemoBlock>
    </section>

    <section id="props">
      <PropsTable :data="propsData" />
    </section>

    <section id="slots">
      <SlotsTable :data="slotsData" />
    </section>
  </ComponentDoc>
</template>
