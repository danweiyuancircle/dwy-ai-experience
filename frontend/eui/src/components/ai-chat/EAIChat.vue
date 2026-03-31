<script setup lang="ts">
import { ref, nextTick, watch } from 'vue'
import { Send } from 'lucide-vue-next'
import { cn } from '@/utils/cn'
import { ESpinner } from '../spinner'
import type { EAIChatProps, EAIChatEmits } from './types'

const props = withDefaults(defineProps<EAIChatProps>(), {
  messages: () => [],
  loading: false,
  placeholder: '输入消息...',
})

const emit = defineEmits<EAIChatEmits>()

const inputValue = ref('')
const messagesContainerRef = ref<HTMLElement | null>(null)

function handleSend() {
  const msg = inputValue.value.trim()
  if (!msg || props.loading) return
  emit('send', msg)
  inputValue.value = ''
}

function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    handleSend()
  }
}

watch(() => props.messages, async () => {
  await nextTick()
  if (messagesContainerRef.value) {
    messagesContainerRef.value.scrollTop = messagesContainerRef.value.scrollHeight
  }
}, { deep: true })
</script>

<template>
  <div
    data-slot="ai-chat"
    :class="cn('flex flex-col h-full border rounded-lg overflow-hidden bg-background', props.class)"
  >
    <!-- Messages area -->
    <div
      ref="messagesContainerRef"
      data-slot="ai-chat-messages"
      class="flex-1 overflow-y-auto p-4 flex flex-col gap-3"
    >
      <template v-if="messages.length === 0">
        <div class="flex-1 flex items-center justify-center text-muted-foreground text-sm">
          暂无消息
        </div>
      </template>

      <div
        v-for="(message, idx) in messages"
        :key="idx"
        :class="cn(
          'flex gap-2 max-w-[80%]',
          message.role === 'user' ? 'self-end flex-row-reverse' : 'self-start',
        )"
      >
        <!-- Avatar -->
        <div
          :class="cn(
            'flex size-7 shrink-0 items-center justify-center rounded-full text-xs font-medium',
            message.role === 'user'
              ? 'bg-primary text-primary-foreground'
              : 'bg-muted text-muted-foreground',
          )"
        >
          {{ message.role === 'user' ? '你' : 'AI' }}
        </div>

        <!-- Content -->
        <div
          :class="cn(
            'rounded-lg px-3 py-2 text-sm',
            message.role === 'user'
              ? 'bg-primary text-primary-foreground'
              : 'bg-muted text-foreground',
          )"
        >
          {{ message.content }}
        </div>
      </div>

      <!-- Loading indicator -->
      <div v-if="loading" class="flex items-center gap-2 self-start">
        <div class="flex size-7 shrink-0 items-center justify-center rounded-full bg-muted">
          <ESpinner size="sm" class="text-muted-foreground" />
        </div>
        <div class="rounded-lg bg-muted px-3 py-2 text-sm text-muted-foreground">
          正在思考...
        </div>
      </div>
    </div>

    <!-- Input area -->
    <div
      data-slot="ai-chat-input"
      class="border-t p-3 flex gap-2 items-end"
    >
      <textarea
        v-model="inputValue"
        :placeholder="placeholder"
        :disabled="loading"
        rows="1"
        class="flex-1 resize-none rounded-md border border-input bg-background px-3 py-2 text-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50 min-h-9 max-h-32"
        @keydown="handleKeydown"
      />
      <button
        type="button"
        :disabled="loading || !inputValue.trim()"
        class="inline-flex size-9 shrink-0 items-center justify-center rounded-md bg-primary text-primary-foreground shadow-xs hover:bg-primary/90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50"
        @click="handleSend"
      >
        <Send class="size-4" />
        <span class="sr-only">发送</span>
      </button>
    </div>
  </div>
</template>
