import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import EAIChat from '@/components/ai-chat/EAIChat.vue'

describe('EAIChat', () => {
  it('renders with default props', () => {
    const wrapper = mount(EAIChat)
    expect(wrapper.find('[data-slot="ai-chat"]').exists()).toBe(true)
  })

  it('shows empty state when no messages', () => {
    const wrapper = mount(EAIChat)
    expect(wrapper.text()).toContain('暂无消息')
  })

  it('renders messages', () => {
    const messages = [
      { role: 'user' as const, content: 'Hello' },
      { role: 'assistant' as const, content: 'Hi there!' },
    ]
    const wrapper = mount(EAIChat, {
      props: { messages },
    })
    expect(wrapper.text()).toContain('Hello')
    expect(wrapper.text()).toContain('Hi there!')
    expect(wrapper.text()).not.toContain('暂无消息')
  })

  it('renders user avatar and assistant avatar', () => {
    const messages = [
      { role: 'user' as const, content: 'Test' },
      { role: 'assistant' as const, content: 'Response' },
    ]
    const wrapper = mount(EAIChat, {
      props: { messages },
    })
    expect(wrapper.text()).toContain('你')
    expect(wrapper.text()).toContain('AI')
  })

  it('shows loading indicator when loading is true', () => {
    const wrapper = mount(EAIChat, {
      props: { loading: true },
    })
    expect(wrapper.text()).toContain('正在思考...')
  })

  it('does not show loading indicator when loading is false', () => {
    const wrapper = mount(EAIChat, {
      props: { loading: false },
    })
    expect(wrapper.text()).not.toContain('正在思考...')
  })

  it('renders custom placeholder on textarea', () => {
    const wrapper = mount(EAIChat, {
      props: { placeholder: 'Ask anything...' },
    })
    const textarea = wrapper.find('textarea')
    expect(textarea.attributes('placeholder')).toBe('Ask anything...')
  })

  it('renders default placeholder on textarea', () => {
    const wrapper = mount(EAIChat)
    const textarea = wrapper.find('textarea')
    expect(textarea.attributes('placeholder')).toBe('输入消息...')
  })
})
