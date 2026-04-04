import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import ETagsInput from '@/components/tags-input/ETagsInput.vue'

describe('ETagsInput', () => {
  it('renders with data-slot attribute', () => {
    const wrapper = mount(ETagsInput)
    expect(wrapper.find('[data-slot="tags-input"]').exists()).toBe(true)
  })

  it('renders tags from modelValue', () => {
    const wrapper = mount(ETagsInput, {
      props: { modelValue: ['Vue', 'React'] },
    })
    const items = wrapper.findAll('[data-slot="tags-input"] span')
    const text = wrapper.text()
    expect(text).toContain('Vue')
    expect(text).toContain('React')
  })

  it('renders input with placeholder', () => {
    const wrapper = mount(ETagsInput, {
      props: { placeholder: '输入标签' },
    })
    const input = wrapper.find('input')
    expect(input.attributes('placeholder')).toBe('输入标签')
  })

  it('applies disabled state', () => {
    const wrapper = mount(ETagsInput, {
      props: { disabled: true },
    })
    const root = wrapper.find('[data-slot="tags-input"]')
    expect(root.attributes('data-disabled')).toBeDefined()
  })

  it('renders empty when modelValue is empty array', () => {
    const wrapper = mount(ETagsInput, {
      props: { modelValue: [] },
    })
    expect(wrapper.find('[data-slot="tags-input"]').exists()).toBe(true)
    expect(wrapper.find('input').exists()).toBe(true)
  })
})
