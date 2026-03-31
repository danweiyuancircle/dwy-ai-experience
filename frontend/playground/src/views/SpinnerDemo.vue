<script setup lang="ts">
import DemoBlock from '../components/DemoBlock.vue'
import ComponentDoc from '../components/ComponentDoc.vue'
import PropsTable from '../components/PropsTable.vue'

const tocItems = [
  { id: 'usage', label: '使用场景' },
  { id: 'sizes', label: '尺寸' },
  { id: 'props', label: 'Props' },
  { id: 'slots', label: 'Slots' },
]

const propsData = [
  { name: 'size', type: "'sm' | 'default' | 'lg'", default: "'default'", description: '加载指示器尺寸' },
  { name: 'class', type: 'string', description: '自定义 CSS 类名，通过 cn() 合并' },
]
</script>

<template>
  <ComponentDoc
    title="Spinner 加载指示器"
    description="旋转加载指示器，支持 sm / default / lg 三种尺寸，用于表示异步操作进行中。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">适用于按钮加载状态、数据请求中、页面加载占位等场景。渲染为 Lucide 的 LoaderCircle 图标并附带旋转动画，自带 role="status" 无障碍属性。</p>
    </section>

    <section id="sizes">
      <DemoBlock
        title="尺寸"
        description="旋转加载指示器，支持 sm / default / lg 三种尺寸"
        code='<ESpinner />
<ESpinner size="lg" />'
      >
        <div class="flex items-center gap-6">
          <div class="flex flex-col items-center gap-2">
            <ESpinner size="sm" />
            <span class="text-xs text-muted-foreground">sm</span>
          </div>
          <div class="flex flex-col items-center gap-2">
            <ESpinner />
            <span class="text-xs text-muted-foreground">default</span>
          </div>
          <div class="flex flex-col items-center gap-2">
            <ESpinner size="lg" />
            <span class="text-xs text-muted-foreground">lg</span>
          </div>
        </div>
      </DemoBlock>
    </section>

    <section id="props">
      <PropsTable :data="propsData" />
    </section>

    <section id="slots">
      <h2 class="text-lg font-semibold mb-3">Slots</h2>
      <p class="text-sm text-muted-foreground">该组件无自定义插槽。</p>
    </section>
  </ComponentDoc>
</template>
