<script setup lang="ts">
import { ref } from 'vue'
import DemoBlock from '../components/DemoBlock.vue'
import ComponentDoc from '../components/ComponentDoc.vue'
import PropsTable from '../components/PropsTable.vue'
import EventsTable from '../components/EventsTable.vue'
import SlotsTable from '../components/SlotsTable.vue'

interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

const messages = ref<ChatMessage[]>([
  { role: 'assistant', content: '你好！我是 AI 助手，有什么可以帮助你的吗？' },
  { role: 'user', content: '请介绍一下 Vue 3 的组合式 API' },
  { role: 'assistant', content: 'Vue 3 的组合式 API（Composition API）是一组函数式 API，让你可以用函数来组织组件逻辑。核心包括 ref、reactive、computed、watch 等响应式 API，以及 onMounted 等生命周期钩子。相比选项式 API，组合式 API 更灵活，更适合复杂组件的逻辑复用。' },
])

const isLoading = ref(false)

const mockReplies = [
  '这是一个很好的问题！让我来解释一下...',
  '根据我的理解，这个问题可以从以下几个方面来分析。',
  '当然可以！我来帮你梳理一下思路。',
  '你提到的这个场景确实很常见，推荐的做法是使用组合式函数来封装逻辑。',
  '没问题，以下是详细的说明和示例代码。',
]

function handleSend(message: string) {
  messages.value.push({ role: 'user', content: message })
  isLoading.value = true
  setTimeout(() => {
    const reply = mockReplies[Math.floor(Math.random() * mockReplies.length)]
    messages.value.push({ role: 'assistant', content: reply })
    isLoading.value = false
  }, 1500)
}

const emptyMessages = ref<ChatMessage[]>([])

function handleEmptySend(message: string) {
  emptyMessages.value.push({ role: 'user', content: message })
  setTimeout(() => {
    emptyMessages.value.push({ role: 'assistant', content: '收到你的消息了！' })
  }, 800)
}

const tocItems = [
  { id: 'usage', label: '使用场景' },
  { id: 'basic', label: '基础聊天' },
  { id: 'empty', label: '空消息状态' },
  { id: 'loading', label: '加载状态' },
  { id: 'props', label: 'Props' },
  { id: 'events', label: 'Events' },
  { id: 'slots', label: 'Slots' },
]

const propsData = [
  { name: 'messages', type: 'ChatMessage[]', default: '[]', description: '消息列表，每项包含 role 和 content' },
  { name: 'loading', type: 'boolean', default: 'false', description: 'AI 回复加载状态，显示"正在思考"提示' },
  { name: 'placeholder', type: 'string', default: "'输入消息...'", description: '输入框占位文字' },
]

const eventsData = [
  { name: 'send', params: '(message: string)', description: '用户发送消息时触发' },
]

const slotsData = [
  { name: 'default', description: '默认插槽' },
]
</script>

<template>
  <ComponentDoc
    title="AIChat AI 对话"
    description="AI 对话界面组件，提供消息展示、输入发送和加载状态，适用于 AI 助手、客服对话等场景。"
    :toc-items="tocItems"
  >
    <section id="usage">
      <h2 class="text-lg font-semibold mb-3">使用场景</h2>
      <p class="text-muted-foreground text-sm leading-relaxed">用于构建 AI 对话交互界面。组件内置用户/AI 消息气泡样式、头像区分、自动滚动到最新消息、Enter 发送等功能。支持 loading 状态显示"正在思考"动画。</p>
    </section>

    <section id="basic">
      <DemoBlock
        title="基础聊天"
        description="包含预设消息的对话界面，发送消息后 AI 会模拟回复"
        code='<EAIChat
  :messages="messages"
  :loading="isLoading"
  placeholder="输入你的问题..."
  @send="handleSend"
/>'
      >
        <div class="h-[400px]">
          <EAIChat
            :messages="messages"
            :loading="isLoading"
            placeholder="输入你的问题..."
            @send="handleSend"
          />
        </div>
      </DemoBlock>
    </section>

    <section id="empty">
      <DemoBlock
        title="空消息状态"
        description="无消息时显示空状态提示，发送消息即开始对话"
        code='<EAIChat :messages="[]" placeholder="说点什么开始对话..." @send="handleSend" />'
      >
        <div class="h-[300px]">
          <EAIChat
            :messages="emptyMessages"
            placeholder="说点什么开始对话..."
            @send="handleEmptySend"
          />
        </div>
      </DemoBlock>
    </section>

    <section id="loading">
      <DemoBlock
        title="加载状态"
        description="AI 回复中显示加载动画"
        code='<EAIChat :messages="messages" :loading="true" />'
      >
        <div class="h-[300px]">
          <EAIChat
            :messages="[
              { role: 'user', content: '帮我生成一个 Vue 3 组件' },
            ]"
            :loading="true"
            placeholder="等待 AI 回复中..."
          />
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
