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
  { name: 'for', type: 'string', description: '关联表单控件的 id，点击标签时聚焦对应控件' },
  { name: 'class', type: 'string', description: '自定义 CSS 类名，通过 cn() 合并' },
]

const slotsData = [
  { name: 'default', description: '标签文本内容' },
]
</script>

<template>
  <ComponentDoc
    title="Label 标签"
    description="用于关联表单控件的标签元素，点击标签可聚焦对应输入框。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">适用于表单中为输入框、选择器等控件添加可点击的文字标签。通过 for 属性与控件 id 关联，提升表单的可用性和无障碍访问性。支持 disabled 状态下自动降低透明度。</p>
    </section>

    <section id="basic">
      <DemoBlock
        title="基础用法"
        description="用于关联表单控件的标签元素"
        code='<ELabel for="inputId">用户名</ELabel>
<EInput id="inputId" placeholder="请输入" />'
      >
        <div class="space-y-4 max-w-sm">
          <div class="space-y-1.5">
            <ELabel for="demo-input">用户名</ELabel>
            <EInput id="demo-input" placeholder="请输入用户名" />
          </div>
          <div class="space-y-1.5">
            <ELabel for="demo-email">邮箱地址</ELabel>
            <EInput id="demo-email" placeholder="请输入邮箱" />
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
