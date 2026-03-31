<script setup lang="ts">
import { ref } from 'vue'
import DemoBlock from '../components/DemoBlock.vue'

const basic = ref('')
const grouped = ref('')
const clearable = ref('vue')
const disabled = ref('react')
const sizeSm = ref('')
const sizeLg = ref('')
const searchValue = ref('')
const multiValue = ref<string[]>([])
const collapseValue = ref<string[]>([])

const fruits = [
  { label: '苹果', value: 'apple' },
  { label: '香蕉', value: 'banana' },
  { label: '橙子', value: 'orange' },
  { label: '草莓', value: 'strawberry' },
  { label: '葡萄', value: 'grape' },
]

const frameworks = [
  {
    label: '前端框架',
    options: [
      { label: 'Vue 3', value: 'vue' },
      { label: 'React', value: 'react' },
      { label: 'Angular', value: 'angular' },
    ],
  },
  {
    label: '后端框架',
    options: [
      { label: 'FastAPI', value: 'fastapi' },
      { label: 'Django', value: 'django' },
      { label: 'Express', value: 'express' },
    ],
  },
]
</script>

<template>
  <div class="max-w-3xl">
    <h1 class="text-2xl font-bold mb-2">Select 选择器</h1>
    <p class="text-muted-foreground mb-6">下拉选择组件，支持单选、分组选项、可清除、禁用等特性。</p>

    <DemoBlock
      title="基础用法"
      description="最简单的下拉选择"
      code='<ESelect v-model="value" :options="options" placeholder="请选择水果" />'
    >
      <div class="space-y-3 max-w-sm">
        <ESelect v-model="basic" :options="fruits" placeholder="请选择水果" />
        <p class="text-sm text-muted-foreground">当前值：{{ basic || '(未选择)' }}</p>
      </div>
    </DemoBlock>

    <DemoBlock
      title="分组选项"
      description="使用 GroupedOption 格式的 options 实现分组"
      code='<ESelect v-model="value" :options="groupedOptions" placeholder="请选择框架" />'
    >
      <div class="space-y-3 max-w-sm">
        <ESelect v-model="grouped" :options="frameworks" placeholder="请选择框架" />
        <p class="text-sm text-muted-foreground">当前值：{{ grouped || '(未选择)' }}</p>
      </div>
    </DemoBlock>

    <DemoBlock
      title="可清除"
      description="设置 clearable 显示清除按钮"
      code='<ESelect v-model="value" :options="options" clearable placeholder="可清除选择" />'
    >
      <div class="max-w-sm">
        <ESelect v-model="clearable" :options="fruits" :clearable="true" placeholder="可清除选择" />
      </div>
    </DemoBlock>

    <DemoBlock
      title="禁用状态"
      description="设置 disabled 禁用选择器"
      code='<ESelect v-model="value" :options="options" :disabled="true" />'
    >
      <div class="max-w-sm">
        <ESelect v-model="disabled" :options="frameworks" :disabled="true" />
      </div>
    </DemoBlock>

    <DemoBlock
      title="尺寸变体"
      description="支持 sm / default / lg 三种尺寸"
      code='<ESelect size="sm" :options="options" placeholder="小尺寸" />
<ESelect :options="options" placeholder="默认尺寸" />
<ESelect size="lg" :options="options" placeholder="大尺寸" />'
    >
      <div class="space-y-3 max-w-sm">
        <ESelect v-model="sizeSm" size="sm" :options="fruits" placeholder="小尺寸 sm" />
        <ESelect :options="fruits" placeholder="默认尺寸 default" />
        <ESelect v-model="sizeLg" size="lg" :options="fruits" placeholder="大尺寸 lg" />
      </div>
    </DemoBlock>

    <DemoBlock
      title="可搜索选择器"
      description="设置 filterable 启用搜索过滤"
      code='<ESelect v-model="searchValue" :options="options" filterable placeholder="输入搜索..." />'
    >
      <div class="space-y-3 max-w-sm">
        <ESelect v-model="searchValue" :options="fruits" filterable placeholder="输入搜索..." />
        <p class="text-sm text-muted-foreground">当前值：{{ searchValue || '(未选择)' }}</p>
      </div>
    </DemoBlock>

    <DemoBlock
      title="多选模式"
      description="设置 multiple 启用多选"
      code='<ESelect v-model="multiValue" :options="options" multiple placeholder="选择多个" />'
    >
      <div class="space-y-3 max-w-sm">
        <ESelect v-model="multiValue" :options="fruits" multiple placeholder="选择多个" />
        <p class="text-sm text-muted-foreground">已选：{{ multiValue.length > 0 ? multiValue.join(', ') : '(未选择)' }}</p>
      </div>
    </DemoBlock>

    <DemoBlock
      title="多选标签折叠"
      description="设置 collapse-tags 折叠多选标签，节省空间"
      code='<ESelect v-model="collapseValue" :options="options" multiple collapse-tags />'
    >
      <div class="space-y-3 max-w-sm">
        <ESelect v-model="collapseValue" :options="fruits" multiple collapse-tags placeholder="选择多个（标签折叠）" />
        <p class="text-sm text-muted-foreground">已选：{{ collapseValue.length > 0 ? collapseValue.join(', ') : '(未选择)' }}</p>
      </div>
    </DemoBlock>
  </div>
</template>
