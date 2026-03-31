<script setup lang="ts">
import { ref } from 'vue'
import DemoBlock from '../components/DemoBlock.vue'

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
</script>

<template>
  <div class="max-w-4xl">
    <h1 class="text-2xl font-bold mb-2">Transfer 穿梭框</h1>
    <p class="text-muted-foreground mb-6">双列表选择组件，用于在两个集合间移动数据项，支持过滤搜索。</p>

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
  </div>
</template>
