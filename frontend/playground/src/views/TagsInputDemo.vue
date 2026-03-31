<script setup lang="ts">
import { ref } from 'vue'
import DemoBlock from '../components/DemoBlock.vue'
import ComponentDoc from '../components/ComponentDoc.vue'
import PropsTable from '../components/PropsTable.vue'
import EventsTable from '../components/EventsTable.vue'
import SlotsTable from '../components/SlotsTable.vue'

const tags1 = ref<string[]>(['Vue', 'TypeScript'])
const tags2 = ref<string[]>(['前端', '后端', '全栈'])
const tagsMax = ref<string[]>(['标签A', 'B标签', '标签C'])
const tagsDisabled = ref<string[]>(['禁用标签1', '禁用标签2'])

const tocItems = [
  { id: 'usage', label: '使用场景' },
  { id: 'basic', label: '基础用法' },
  { id: 'sizes', label: '尺寸变体' },
  { id: 'max', label: '数量限制' },
  { id: 'disabled', label: '禁用状态' },
  { id: 'props', label: 'Props' },
  { id: 'events', label: 'Events' },
  { id: 'slots', label: 'Slots' },
]

const propsData = [
  { name: 'modelValue', type: 'string[]', description: '绑定的标签数组' },
  { name: 'placeholder', type: 'string', description: '输入框占位提示文字' },
  { name: 'max', type: 'number', description: '最多可添加的标签数量' },
  { name: 'disabled', type: 'boolean', default: 'false', description: '是否禁用' },
  { name: 'size', type: "'sm' | 'default' | 'lg'", default: "'default'", description: '组件尺寸' },
  { name: 'class', type: 'string', description: '自定义 CSS 类名' },
]

const eventsData = [
  { name: 'update:modelValue', params: '(value: string[])', description: '标签数组变化时触发（用于 v-model）' },
  { name: 'change', params: '(value: string[])', description: '标签数组变化时触发' },
]

const slotsData = [
  { name: 'tag', props: '{ tag: string, index: number, remove: () => void }', description: '自定义标签渲染内容' },
]
</script>

<template>
  <ComponentDoc
    title="TagsInput 标签输入"
    description="标签输入组件，可键入文字后按 Enter 添加标签，支持最大数量限制。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">适用于需要用户输入多个标签或关键词的场景，如文章标签编辑、技能标签录入、邮件收件人输入等。通过 max 属性可以限制标签数量上限，避免用户过度添加。</p>
    </section>

    <section id="basic">
      <DemoBlock
        title="基础用法"
        description="输入文字后按 Enter 或逗号添加标签，点击 x 删除"
        code='<ETagsInput v-model="tags" placeholder="输入后按 Enter 添加" />'
      >
        <div class="space-y-3 max-w-sm">
          <ETagsInput v-model="tags1" placeholder="输入技术栈后按 Enter" />
          <p class="text-sm text-muted-foreground">当前标签：{{ tags1.join(', ') || '(空)' }}</p>
        </div>
      </DemoBlock>
    </section>

    <section id="sizes">
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
    </section>

    <section id="max">
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
    </section>

    <section id="disabled">
      <DemoBlock
        title="禁用状态"
        description="设置 disabled 禁用输入"
        code='<ETagsInput v-model="tags" :disabled="true" />'
      >
        <div class="max-w-sm">
          <ETagsInput v-model="tagsDisabled" :disabled="true" placeholder="禁用状态" />
        </div>
      </DemoBlock>
    </section>

    <section id="props">
      <PropsTable :data="propsData" />
    </section>

    <section id="events">
      <EventsTable :data="eventsData" />
    </section>

    <section id="slots">
      <SlotsTable :data="slotsData" />
    </section>
  </ComponentDoc>
</template>
