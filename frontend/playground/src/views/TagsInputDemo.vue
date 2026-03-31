<script setup lang="ts">
import { ref } from 'vue'
import DemoBlock from '../components/DemoBlock.vue'

const tags1 = ref<string[]>(['Vue', 'TypeScript'])
const tags2 = ref<string[]>(['前端', '后端', '全栈'])
const tagsMax = ref<string[]>(['标签A', 'B标签', '标签C'])
const tagsDisabled = ref<string[]>(['禁用标签1', '禁用标签2'])
</script>

<template>
  <div class="max-w-3xl">
    <h1 class="text-2xl font-bold mb-2">TagsInput 标签输入</h1>
    <p class="text-muted-foreground mb-6">标签输入组件，可键入文字后按 Enter 添加标签，支持最大数量限制。</p>

    <DemoBlock
      title="基础用法"
      description="输入文字后按 Enter 或逗号添加标签，点击 × 删除"
      code='<ETagsInput v-model="tags" placeholder="输入后按 Enter 添加" />'
    >
      <div class="space-y-3 max-w-sm">
        <ETagsInput v-model="tags1" placeholder="输入技术栈后按 Enter" />
        <p class="text-sm text-muted-foreground">当前标签：{{ tags1.join(', ') || '(空)' }}</p>
      </div>
    </DemoBlock>

    <DemoBlock
      title="尺寸变体"
      description="支持 sm / default / lg 三种尺寸"
      code='<ETagsInput v-model="tags" size="sm" />
<ETagsInput v-model="tags" />
<ETagsInput v-model="tags" size="lg" />'
    >
      <div class="space-y-3 max-w-sm">
        <ETagsInput v-model="tags2" size="sm" placeholder="小尺寸 sm" />
        <ETagsInput v-model="tags2" placeholder="默认尺寸" />
        <ETagsInput v-model="tags2" size="lg" placeholder="大尺寸 lg" />
      </div>
    </DemoBlock>

    <DemoBlock
      title="最大数量限制"
      description="通过 max 限制最多标签数量"
      code='<ETagsInput v-model="tags" :max="3" placeholder="最多添加 3 个" />'
    >
      <div class="space-y-3 max-w-sm">
        <ETagsInput v-model="tagsMax" :max="3" placeholder="最多添加 3 个标签" />
        <p class="text-sm text-muted-foreground">{{ tagsMax.length }}/3 个标签</p>
      </div>
    </DemoBlock>

    <DemoBlock
      title="禁用状态"
      description="设置 disabled 禁用输入"
      code='<ETagsInput v-model="tags" :disabled="true" />'
    >
      <div class="max-w-sm">
        <ETagsInput v-model="tagsDisabled" :disabled="true" placeholder="禁用状态" />
      </div>
    </DemoBlock>
  </div>
</template>
