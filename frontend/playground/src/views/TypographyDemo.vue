<script setup lang="ts">
import DemoBlock from '../components/DemoBlock.vue'
import ComponentDoc from '../components/ComponentDoc.vue'
import PropsTable from '../components/PropsTable.vue'
import SlotsTable from '../components/SlotsTable.vue'

const tocItems = [
  { id: 'usage', label: '使用场景' },
  { id: 'variants', label: '排版变体' },
  { id: 'custom-tag', label: '自定义标签' },
  { id: 'props', label: 'Props' },
  { id: 'slots', label: 'Slots' },
]

const propsData = [
  { name: 'variant', type: "'h1' | 'h2' | 'h3' | 'h4' | 'p' | 'lead' | 'large' | 'small' | 'muted'", default: "'p'", description: '排版变体，决定标签和样式' },
  { name: 'as', type: 'string', description: '自定义渲染的 HTML 标签，覆盖 variant 默认标签' },
  { name: 'class', type: 'string', description: '自定义 CSS 类名，通过 cn() 合并' },
]

const slotsData = [
  { name: 'default', description: '文本内容' },
]
</script>

<template>
  <ComponentDoc
    title="Typography 排版"
    description="提供 h1-h4、p、lead、large、small、muted 等排版变体，自动映射对应 HTML 标签和样式。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">适用于页面标题、段落正文、辅助说明等文字排版场景。通过 variant 属性统一管理字体大小、行高、间距等样式，避免在各处手写 Tailwind 类名。支持 h1-h4 标题、p 正文、lead 导语、large/small 辅助文字、muted 次要文字。</p>
    </section>

    <section id="variants">
      <DemoBlock
        title="排版变体"
        description="提供 h1-h4、p、lead、large、small、muted 等排版变体"
        code='<ETypography variant="h1">大标题</ETypography>
<ETypography variant="p">正文段落</ETypography>
<ETypography variant="muted">静音文字</ETypography>'
      >
        <div class="space-y-3">
          <ETypography variant="h1">H1 大标题</ETypography>
          <ETypography variant="h2">H2 二级标题</ETypography>
          <ETypography variant="h3">H3 三级标题</ETypography>
          <ETypography variant="h4">H4 四级标题</ETypography>
          <ETypography variant="lead">Lead 导语文字，比正文大一些</ETypography>
          <ETypography variant="p">P 正文段落，这是一段普通的正文内容，用于展示段落样式。</ETypography>
          <ETypography variant="large">Large 较大文字</ETypography>
          <ETypography variant="small">Small 较小文字</ETypography>
          <ETypography variant="muted">Muted 静音文字，颜色较浅</ETypography>
        </div>
      </DemoBlock>
    </section>

    <section id="custom-tag">
      <DemoBlock
        title="自定义标签"
        description="通过 as 属性覆盖默认 HTML 标签"
        code='<ETypography variant="h2" as="div">用 div 渲染的 h2 样式</ETypography>
<ETypography variant="muted" as="span">用 span 渲染的 muted 样式</ETypography>'
      >
        <div class="space-y-3">
          <ETypography variant="h2" as="div">用 div 渲染的 h2 样式</ETypography>
          <ETypography variant="muted" as="span">用 span 渲染的 muted 样式</ETypography>
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
