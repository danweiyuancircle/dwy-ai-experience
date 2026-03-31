<script setup lang="ts">
import { ref } from 'vue'
import DemoBlock from '../components/DemoBlock.vue'

const singleCheck = ref(false)
const indeterminate = ref(true)
const disabledCheck = ref(false)

const radioValue = ref('vue')
const radioValueVertical = ref('react')
const radioDisabled = ref('angular')

const frameworks = [
  { label: 'Vue 3', value: 'vue' },
  { label: 'React', value: 'react' },
  { label: 'Angular', value: 'angular' },
  { label: 'Svelte', value: 'svelte' },
]
</script>

<template>
  <div class="max-w-3xl">
    <h1 class="text-2xl font-bold mb-2">Checkbox & Radio</h1>
    <p class="text-muted-foreground mb-6">复选框和单选框组件，支持单选/多选场景。</p>

    <DemoBlock
      title="基础复选框"
      description="单个复选框，支持 label 文本显示"
      code='<ECheckbox v-model="checked" label="同意服务条款" />'
    >
      <div class="space-y-3">
        <ECheckbox v-model="singleCheck" label="同意服务条款" />
        <p class="text-sm text-muted-foreground">当前状态：{{ singleCheck ? '已勾选' : '未勾选' }}</p>
      </div>
    </DemoBlock>

    <DemoBlock
      title="不确定状态"
      description="通过 indeterminate 属性设置半选状态（常用于全选场景）"
      code='<ECheckbox :indeterminate="true" label="全选（半选状态）" />'
    >
      <ECheckbox v-model="indeterminate" :indeterminate="true" label="全选（半选状态）" />
    </DemoBlock>

    <DemoBlock
      title="禁用状态"
      description="disabled 禁用复选框交互"
      code='<ECheckbox :disabled="true" label="禁用（未选）" />
<ECheckbox :modelValue="true" :disabled="true" label="禁用（已选）" />'
    >
      <div class="flex gap-4">
        <ECheckbox v-model="disabledCheck" :disabled="true" label="禁用（未选）" />
        <ECheckbox :modelValue="true" :disabled="true" label="禁用（已选）" />
      </div>
    </DemoBlock>

    <DemoBlock
      title="Radio 单选（水平）"
      description="通过 options 数组渲染单选组，默认水平排列"
      code='<ERadio v-model="value" :options="options" />'
    >
      <div class="space-y-3">
        <ERadio v-model="radioValue" :options="frameworks" />
        <p class="text-sm text-muted-foreground">当前选择：{{ radioValue }}</p>
      </div>
    </DemoBlock>

    <DemoBlock
      title="Radio 单选（垂直）"
      description="设置 direction='vertical' 垂直排列"
      code='<ERadio v-model="value" :options="options" direction="vertical" />'
    >
      <div class="space-y-3">
        <ERadio v-model="radioValueVertical" :options="frameworks" direction="vertical" />
        <p class="text-sm text-muted-foreground">当前选择：{{ radioValueVertical }}</p>
      </div>
    </DemoBlock>

    <DemoBlock
      title="Radio 禁用状态"
      description="设置 disabled 禁用整个单选组"
      code='<ERadio v-model="value" :options="options" :disabled="true" />'
    >
      <ERadio v-model="radioDisabled" :options="frameworks" :disabled="true" />
    </DemoBlock>
  </div>
</template>
