<script setup lang="ts">
import DemoBlock from '../components/DemoBlock.vue'
</script>

<template>
  <div class="max-w-3xl">
    <h1 class="text-2xl font-bold mb-2">Typography 排版</h1>
    <p class="text-muted-foreground mb-6">提供 h1-h4、p、lead、large、small、muted 等排版变体。</p>

    <DemoBlock
      title="Typography 排版"
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
  </div>
</template>
