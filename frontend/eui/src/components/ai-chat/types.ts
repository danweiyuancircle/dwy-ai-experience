/**
 * EAIChat AI 对话组件的类型定义
 */
import type { HTMLAttributes } from 'vue'

/**
 * 单条对话消息
 */
export interface ChatMessage {
  /** 消息发送方：user=用户，assistant=AI 助手 */
  role: 'user' | 'assistant'
  /** 消息文本内容 */
  content: string
}

/**
 * EAIChat AI 对话组件 Props
 */
export interface EAIChatProps {
  /** 自定义 class，透传到根容器 */
  class?: HTMLAttributes['class']
  /** 消息列表，由外部维护 */
  messages?: ChatMessage[]
  /** AI 是否正在回复中（展示"正在思考"并禁用输入） */
  loading?: boolean
  /** 输入框占位文本 */
  placeholder?: string
}

/**
 * EAIChat AI 对话组件事件
 */
export interface EAIChatEmits {
  /** 用户发送消息时触发，参数为文本内容（已 trim） */
  send: [message: string]
}
