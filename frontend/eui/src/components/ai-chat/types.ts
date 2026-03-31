import type { HTMLAttributes } from 'vue'

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

export interface EAIChatProps {
  class?: HTMLAttributes['class']
  messages?: ChatMessage[]
  loading?: boolean
  placeholder?: string
}

export interface EAIChatEmits {
  send: [message: string]
}
