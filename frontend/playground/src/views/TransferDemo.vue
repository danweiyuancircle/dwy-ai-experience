<script setup lang="ts">
import { ref } from 'vue'
import DemoBlock from '../components/DemoBlock.vue'
import ComponentDoc from '../components/ComponentDoc.vue'
import PropsTable from '../components/PropsTable.vue'
import EventsTable from '../components/EventsTable.vue'

const selected1 = ref<(string | number)[]>(['vue', 'ts'])
const selected2 = ref<(string | number)[]>([])

const techData = [
  { label: 'Vue 3', value: 'vue' },
  { label: 'React', value: 'react' },
  { label: 'TypeScript', value: 'ts' },
  { label: 'JavaScript', value: 'js' },
  { label: 'Node.js', value: 'node' },
  { label: 'Python', value: 'python' },
  { label: 'Go', value: 'go' },
  { label: 'Rust', value: 'rust', disabled: true },
]

const roleData = [
  { label: '前端开发', value: 'frontend' },
  { label: '后端开发', value: 'backend' },
  { label: '全栈开发', value: 'fullstack' },
  { label: '移动端开发', value: 'mobile' },
  { label: 'UI/UX 设计', value: 'design' },
  { label: '产品经理', value: 'pm' },
  { label: '数据分析', value: 'data' },
  { label: '测试工程师', value: 'qa' },
]

const tocItems = [
  { id: 'usage', label: '使用场景' },
  { id: 'basic', label: '基础穿梭框' },
  { id: 'filterable', label: '可过滤穿梭框' },
  { id: 'props', label: 'Props' },
  { id: 'events', label: 'Events' },
]

const propsData = [
  { name: 'modelValue', type: '(string | number)[]', default: '[]', description: '已选项的 value 数组，支持 v-model' },
  { name: 'data', type: 'TransferItem[]', default: '[]', description: '穿梭框数据源，每项包含 label、value、disabled' },
  { name: 'filterable', type: 'boolean', default: 'false', description: '是否显示搜索过滤框' },
  { name: 'titles', type: '[string, string]', default: '-', description: '左右列表标题，如 ["可选", "已选"]' },
  { name: 'class', type: 'string', default: '-', description: '自定义 CSS 类名' },
]

const eventsData = [
  { name: 'update:modelValue', params: '(value: (string | number)[])', description: '已选项变更时触发' },
  { name: 'change', params: '(value: (string | number)[], direction: "right" | "left", moved: (string | number)[])', description: '数据项移动时触发，包含移动方向和被移动的项' },
]
</script>

<template>
  <ComponentDoc
    title="Transfer 穿梭框"
    description="双列表选择组件，用于在两个集合间移动数据项，支持过滤搜索。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">适用于需要在两个列表之间批量移动数据项的场景，如权限分配、角色选择、技术栈配置等。左侧显示全部候选项，右侧显示已选项，通过中间的操作按钮进行双向移动。支持搜索过滤和禁用指定项。</p>
    </section>

    <section id="basic">
      <DemoBlock
        title="基础穿梭框"
        description="左侧显示全部候选项，右侧显示已选项"
        code='<ETransfer v-model="selected" :data="data" />'
      >
        <div class="space-y-3">
          <ETransfer v-model="selected1" :data="techData" :titles="['可选技术栈', '已选技术栈']" />
          <p class="text-sm text-muted-foreground">已选：{{ selected1.join(', ') || '(未选择)' }}</p>
        </div>
      </DemoBlock>
    </section>

    <section id="filterable">
      <DemoBlock
        title="可过滤的穿梭框"
        description="设置 filterable 显示搜索框，快速过滤列表"
        code='<ETransfer v-model="selected" :data="data" :filterable="true" />'
      >
        <ETransfer
          v-model="selected2"
          :data="roleData"
          :filterable="true"
          :titles="['所有职位', '已选职位']"
        />
      </DemoBlock>
    </section>

    <section id="props">
      <PropsTable :data="propsData" />
    </section>

    <section id="events">
      <EventsTable :data="eventsData" />
    </section>
  </ComponentDoc>
</template>
