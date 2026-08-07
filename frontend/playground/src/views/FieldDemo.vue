<script setup lang="ts">
import { ref } from 'vue'
import DemoBlock from '../components/DemoBlock.vue'
import ComponentDoc from '../components/ComponentDoc.vue'
import PropsTable from '../components/PropsTable.vue'
import SlotsTable from '../components/SlotsTable.vue'

const name = ref('')
const invalidName = ref('')

const tocItems = [
  { id: 'usage', label: '使用场景' },
  { id: 'basic', label: '基础用法' },
  { id: 'invalid', label: '错误态' },
  { id: 'props', label: 'Props' },
  { id: 'slots', label: 'Slots' },
]

const propsData = [
  { name: 'orientation', type: "'vertical' | 'horizontal' | 'responsive'", default: "'vertical'", description: 'label 与控件的排列方向' },
  { name: 'invalid', type: 'boolean', default: 'false', description: '是否处于校验失败态（红色样式）' },
  { name: 'class', type: 'string', default: '—', description: '自定义 CSS 类名' },
]

const slotsData = [
  { name: 'default', description: '字段内容：通常放 Label + 控件 + 描述/错误文案' },
]
</script>

<template>
  <ComponentDoc
    title="Field 字段容器"
    description="表单字段的布局容器，提供 label / control / description 结构，通过 invalid 驱动错误态。自身不参与校验。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">
        需要统一字段间距与错误态样式、又不想引入完整 EForm 时，用 EField 包一层即可。
        完整表单校验场景优先用 EForm + EFormItem。
      </p>
    </section>

    <section id="basic">
      <DemoBlock
        title="基础用法"
        description="纵向排列 label 与输入框"
        code='<EField>
  <ELabel>用户名</ELabel>
  <EInput v-model="name" placeholder="请输入" />
</EField>'
      >
        <EField class="max-w-sm">
          <ELabel>用户名</ELabel>
          <EInput v-model="name" placeholder="请输入" />
          <p class="text-xs text-muted-foreground">展示名，2–32 字符</p>
        </EField>
      </DemoBlock>
    </section>

    <section id="invalid">
      <DemoBlock
        title="错误态"
        description="invalid 时容器与文字切到 destructive 色"
        code='<EField invalid>
  <ELabel>用户名</ELabel>
  <EInput v-model="name" />
  <p class="text-xs">不能为空</p>
</EField>'
      >
        <EField invalid class="max-w-sm">
          <ELabel>用户名</ELabel>
          <EInput v-model="invalidName" placeholder="请输入" />
          <p class="text-xs">不能为空</p>
        </EField>
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
