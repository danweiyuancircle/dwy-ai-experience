<script setup lang="ts">
import DemoBlock from '../components/DemoBlock.vue'
import ComponentDoc from '../components/ComponentDoc.vue'
import PropsTable from '../components/PropsTable.vue'
import SlotsTable from '../components/SlotsTable.vue'

const tocItems = [
  { id: 'usage', label: '使用场景' },
  { id: 'basic', label: '基础用法' },
  { id: 'props', label: 'Props' },
  { id: 'slots', label: 'Slots' },
]

const propsData = [
  { name: 'size', type: "'sm' | 'default' | 'lg'", default: "'default'", description: '全局默认尺寸，子组件未显式指定时继承' },
  { name: 'zIndex', type: 'number', default: '2000', description: '弹层 z-index 基础值' },
  { name: 'locale', type: 'Record<string, string>', default: '—', description: '国际化文案覆盖，与内置 defaultLocale 合并' },
]

const slotsData = [
  { name: 'default', description: '应用内容，建议放在 App 根节点' },
]
</script>

<template>
  <ComponentDoc
    title="ConfigProvider 全局配置"
    description="向子树注入 size / zIndex / locale。应用根节点必须包裹，日期选择器、弹层层级与默认文案依赖此组件。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">
        每个使用 EUI 的应用在根组件必须挂载 <code class="text-xs bg-muted px-1 rounded">EConfigProvider</code>。
        缺省会导致日期/日历英文、z-index 不协调、UI 文案回退默认值。详见集成指南。
      </p>
    </section>

    <section id="basic">
      <DemoBlock
        title="根节点包裹"
        description="推荐写在 main 入口或 App.vue 最外层"
        code='<EConfigProvider size="default" :z-index="2000">
  <RouterView />
</EConfigProvider>'
      >
        <div class="rounded-md border bg-muted/40 p-4 text-sm space-y-2">
          <p>当前预览站已在应用根挂载 ConfigProvider。</p>
          <p class="text-muted-foreground">可通过 props 覆盖全局 size / zIndex / locale。</p>
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
