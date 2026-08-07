<script setup lang="ts">
import DemoBlock from '../components/DemoBlock.vue'
import ComponentDoc from '../components/ComponentDoc.vue'
import PropsTable from '../components/PropsTable.vue'
import SlotsTable from '../components/SlotsTable.vue'

const tocItems = [
  { id: 'usage', label: '使用场景' },
  { id: 'basic', label: '基础用法' },
  { id: 'variants', label: '变体' },
  { id: 'props', label: 'Props' },
  { id: 'slots', label: 'Slots' },
]

const propsData = [
  { name: 'variant', type: "'default' | 'outline' | 'muted'", default: "'default'", description: '视觉变体' },
  { name: 'size', type: "'default' | 'sm'", default: "'default'", description: '内边距与间距' },
  { name: 'as', type: 'string', default: "'div'", description: '渲染的 HTML 标签' },
  { name: 'class', type: 'string', default: '—', description: '自定义 CSS 类名' },
]

const slotsData = [
  { name: 'default', description: '列表项内容' },
]
</script>

<template>
  <ComponentDoc
    title="Item 列表项"
    description="通用列表项容器，统一圆角、边框与间距，适合设置页、选择列表等场景。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">
        需要一致的单行/多行条目外观时使用。不绑定业务数据模型，纯布局与样式。
      </p>
    </section>

    <section id="basic">
      <DemoBlock
        title="基础用法"
        description="默认透明背景条目"
        code='<EItem>
  <div class="font-medium">通知设置</div>
  <div class="text-sm text-muted-foreground">管理推送与邮件</div>
</EItem>'
      >
        <div class="max-w-md space-y-2">
          <EItem>
            <div>
              <div class="font-medium">通知设置</div>
              <div class="text-sm text-muted-foreground">管理推送与邮件</div>
            </div>
          </EItem>
          <EItem>
            <div>
              <div class="font-medium">隐私</div>
              <div class="text-sm text-muted-foreground">可见性与数据</div>
            </div>
          </EItem>
        </div>
      </DemoBlock>
    </section>

    <section id="variants">
      <DemoBlock
        title="变体"
        description="outline / muted"
        code='<EItem variant="outline">...</EItem>
<EItem variant="muted" size="sm">...</EItem>'
      >
        <div class="max-w-md space-y-2">
          <EItem variant="outline">
            <span class="text-sm">outline 边框</span>
          </EItem>
          <EItem variant="muted" size="sm">
            <span class="text-sm">muted 小尺寸</span>
          </EItem>
        </div>
      </DemoBlock>
    </section>

    <section id="props">
      <h2 class="text-lg font-semibold mb-3">Props</h2>
      <PropsTable :data="propsData" />
    </section>

    <section id="slots">
      <h2 class="text-lg font-semibold mb-3">Slots</h2>
      <SlotsTable :data="slotsData" />
    </section>
  </ComponentDoc>
</template>
