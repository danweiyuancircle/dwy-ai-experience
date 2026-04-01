<script setup lang="ts">
import DemoBlock from '../components/DemoBlock.vue'
import ComponentDoc from '../components/ComponentDoc.vue'
import PropsTable from '../components/PropsTable.vue'
import SlotsTable from '../components/SlotsTable.vue'

const tocItems = [
  { id: 'usage', label: '使用场景' },
  { id: 'badge-variants', label: 'Badge 变体' },
  { id: 'badge-usage', label: 'Badge 使用场景' },
  { id: 'props', label: 'Props' },
  { id: 'slots', label: 'Slots' },
]

const propsData = [
  { name: 'variant', type: "'default' | 'secondary' | 'destructive' | 'outline'", default: "'default'", description: '徽标样式变体' },
  { name: 'class', type: 'string', default: '-', description: '自定义 CSS 类名' },
]

const slotsData = [
  { name: 'default', description: '徽标文字内容' },
]
</script>

<template>
  <ComponentDoc
    title="Badge 徽标"
    description="Badge 用于状态标记和数量显示，如在职/离职状态、版本标识、未读消息数等。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">Badge 适用于状态标记（在职/离职）、版本标识（Beta/弃用）、数量显示（未读消息数）等场景。支持 default、secondary、destructive、outline 四种样式变体。</p>
    </section>

    <section id="badge-variants">
      <DemoBlock
        title="Badge 变体"
        description="4 种徽标样式：default、secondary、destructive、outline"
        code='<EBadge>默认</EBadge>
<EBadge variant="secondary">次要</EBadge>
<EBadge variant="destructive">危险</EBadge>
<EBadge variant="outline">描边</EBadge>'
      >
        <div class="flex flex-wrap gap-3">
          <EBadge>默认</EBadge>
          <EBadge variant="secondary">次要</EBadge>
          <EBadge variant="destructive">危险</EBadge>
          <EBadge variant="outline">描边</EBadge>
        </div>
      </DemoBlock>
    </section>

    <section id="badge-usage">
      <DemoBlock
        title="Badge 使用场景"
        description="常见的徽标应用场景"
      >
        <div class="space-y-4">
          <div class="flex flex-wrap gap-2">
            <EBadge>在职</EBadge>
            <EBadge variant="secondary">休假</EBadge>
            <EBadge variant="outline">兼职</EBadge>
            <EBadge variant="destructive">离职</EBadge>
          </div>
          <div class="flex flex-wrap gap-2">
            <EBadge variant="outline">v1.0.0</EBadge>
            <EBadge variant="secondary">Beta</EBadge>
            <EBadge variant="destructive">弃用</EBadge>
          </div>
          <div class="flex items-center gap-2">
            <span class="text-sm font-medium">未读消息</span>
            <EBadge variant="destructive">12</EBadge>
          </div>
        </div>
      </DemoBlock>
    </section>

    <section id="props">
      <h2 class="text-lg font-semibold mb-3">Badge Props</h2>
      <PropsTable :data="propsData" />
    </section>

    <section id="slots">
      <SlotsTable :data="slotsData" />
    </section>
  </ComponentDoc>
</template>
