<script setup lang="ts">
import DemoBlock from '../components/DemoBlock.vue'
import ComponentDoc from '../components/ComponentDoc.vue'
import PropsTable from '../components/PropsTable.vue'
import SlotsTable from '../components/SlotsTable.vue'

const tocItems = [
  { id: 'usage', label: '使用场景' },
  { id: 'shortcuts', label: '快捷键展示' },
  { id: 'props', label: 'Props' },
  { id: 'slots', label: 'Slots' },
]

const propsData = [
  { name: 'class', type: 'string', description: '自定义 CSS 类名，通过 cn() 合并' },
]

const slotsData = [
  { name: 'default', description: '按键文本或图标内容' },
]
</script>

<template>
  <ComponentDoc
    title="Kbd 键盘按键"
    description="用于展示快捷键的键盘样式组件，以内联方式呈现按键符号。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">适用于文档说明、帮助面板、功能提示中展示键盘快捷键。可以组合多个 Kbd 组件表示组合键，如 Ctrl+C、Cmd+K 等。组件渲染为语义化的 &lt;kbd&gt; 标签。</p>
    </section>

    <section id="shortcuts">
      <DemoBlock
        title="快捷键展示"
        description="用于展示快捷键的键盘样式组件"
        code='<EKbd>Ctrl</EKbd> + <EKbd>C</EKbd>'
      >
        <div class="space-y-4">
          <div class="flex items-center gap-2 text-sm">
            <EKbd>Ctrl</EKbd>
            <span>+</span>
            <EKbd>C</EKbd>
            <span class="text-muted-foreground ml-2">复制</span>
          </div>
          <div class="flex items-center gap-2 text-sm">
            <EKbd>Ctrl</EKbd>
            <span>+</span>
            <EKbd>V</EKbd>
            <span class="text-muted-foreground ml-2">粘贴</span>
          </div>
          <div class="flex items-center gap-2 text-sm">
            <EKbd>⌘</EKbd>
            <span>+</span>
            <EKbd>K</EKbd>
            <span class="text-muted-foreground ml-2">打开命令面板</span>
          </div>
          <div class="flex items-center gap-2 text-sm">
            <EKbd>Escape</EKbd>
            <span class="text-muted-foreground ml-2">关闭对话框</span>
          </div>
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
