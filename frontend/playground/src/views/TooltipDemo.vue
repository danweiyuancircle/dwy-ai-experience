<script setup lang="ts">
import DemoBlock from '../components/DemoBlock.vue'
import ComponentDoc from '../components/ComponentDoc.vue'
import PropsTable from '../components/PropsTable.vue'
import SlotsTable from '../components/SlotsTable.vue'

const tocItems = [
  { id: 'usage', label: '使用场景' },
  { id: 'tooltip-basic', label: '基础用法' },
  { id: 'tooltip-delay', label: '延迟显示' },
  { id: 'props', label: 'Props' },
  { id: 'slots', label: 'Slots' },
]

const propsData = [
  { name: 'content', type: 'string', default: '-', description: '提示文字内容' },
  { name: 'side', type: "'top' | 'right' | 'bottom' | 'left'", default: "'top'", description: '弹出方向' },
  { name: 'sideOffset', type: 'number', default: '-', description: '与触发元素的间距（px）' },
  { name: 'delayDuration', type: 'number', default: '-', description: '悬停后延迟显示的时间（毫秒）' },
  { name: 'disabled', type: 'boolean', default: 'false', description: '是否禁用 Tooltip' },
  { name: 'class', type: 'string', default: '-', description: '自定义 CSS 类名' },
]

const slotsData = [
  { name: 'default', description: '触发 Tooltip 的目标元素' },
]
</script>

<template>
  <ComponentDoc
    title="Tooltip 文字提示"
    description="Tooltip 用于鼠标悬停时展示简短文字说明，如图标按钮的功能提示、表格列标题的完整文本等。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">Tooltip 适用于鼠标悬停时展示简短文字说明，如图标按钮的功能提示、表格列标题的完整文本等。</p>
    </section>

    <section id="tooltip-basic">
      <DemoBlock
        title="基础用法"
        description="悬停时显示简短提示文字"
        code='<ETooltip content="这是一条提示信息">
  <EButton>悬停查看提示</EButton>
</ETooltip>'
      >
        <div class="flex flex-wrap gap-3">
          <ETooltip content="这是顶部提示" side="top">
            <EButton variant="outline">顶部 Top</EButton>
          </ETooltip>
          <ETooltip content="这是底部提示" side="bottom">
            <EButton variant="outline">底部 Bottom</EButton>
          </ETooltip>
          <ETooltip content="这是左侧提示" side="left">
            <EButton variant="outline">左侧 Left</EButton>
          </ETooltip>
          <ETooltip content="这是右侧提示" side="right">
            <EButton variant="outline">右侧 Right</EButton>
          </ETooltip>
        </div>
      </DemoBlock>
    </section>

    <section id="tooltip-delay">
      <DemoBlock
        title="延迟显示"
        description="通过 delayDuration 控制显示延迟（毫秒）"
        code='<ETooltip content="延迟 500ms 显示" :delayDuration="500">
  <EButton>延迟 Tooltip</EButton>
</ETooltip>'
      >
        <div class="flex gap-3">
          <ETooltip content="即时显示（0ms）" :delayDuration="0">
            <EButton variant="outline" size="sm">即时</EButton>
          </ETooltip>
          <ETooltip content="延迟 300ms 显示" :delayDuration="300">
            <EButton variant="outline" size="sm">300ms 延迟</EButton>
          </ETooltip>
          <ETooltip content="延迟 800ms 显示" :delayDuration="800">
            <EButton variant="outline" size="sm">800ms 延迟</EButton>
          </ETooltip>
        </div>
      </DemoBlock>
    </section>

    <section id="props">
      <h2 class="text-lg font-semibold mb-3">Tooltip Props</h2>
      <PropsTable :data="propsData" />
    </section>

    <section id="slots">
      <h2 class="text-lg font-semibold mb-3">Tooltip Slots</h2>
      <SlotsTable :data="slotsData" />
    </section>
  </ComponentDoc>
</template>
