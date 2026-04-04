import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import EMention from '@/components/mention/EMention.vue'

describe('EMention', () => {
  it('renders a textarea element', () => {
    const wrapper = mount(EMention)
    expect(wrapper.find('textarea').exists()).toBe(true)
  })

  it('displays the provided modelValue', () => {
    const wrapper = mount(EMention, {
      props: { modelValue: 'hello world' },
    })
    expect(wrapper.find('textarea').element.value).toBe('hello world')
  })

  it('emits update:modelValue on input', async () => {
    const wrapper = mount(EMention)
    const textarea = wrapper.find('textarea')
    // Manually set value and trigger input event
    textarea.element.value = 'test input'
    await textarea.trigger('input')
    expect(wrapper.emitted('update:modelValue')?.[0]).toEqual(['test input'])
  })

  it('applies placeholder prop', () => {
    const wrapper = mount(EMention, {
      props: { placeholder: '请输入内容' },
    })
    expect(wrapper.find('textarea').attributes('placeholder')).toBe('请输入内容')
  })

  it('applies disabled attribute', () => {
    const wrapper = mount(EMention, {
      props: { disabled: true },
    })
    expect(wrapper.find('textarea').attributes('disabled')).toBeDefined()
  })

  it('accepts options prop without error', () => {
    const options = [
      { label: 'Alice', value: 'alice' },
      { label: 'Bob', value: 'bob' },
    ]
    const wrapper = mount(EMention, {
      props: { options },
    })
    expect(wrapper.find('textarea').exists()).toBe(true)
  })

  it('does not show dropdown when textarea is empty', () => {
    const wrapper = mount(EMention, {
      props: {
        options: [
          { label: 'Alice', value: 'alice' },
        ],
      },
    })
    // No dropdown visible initially
    expect(wrapper.find('ul').exists()).toBe(false)
  })

  it('applies custom class to root element', () => {
    const wrapper = mount(EMention, {
      props: { class: 'mention-custom' },
    })
    expect(wrapper.classes()).toContain('mention-custom')
  })

  it('updates textarea when modelValue prop changes', async () => {
    const wrapper = mount(EMention, {
      props: { modelValue: 'initial' },
    })
    expect(wrapper.find('textarea').element.value).toBe('initial')

    await wrapper.setProps({ modelValue: 'updated' })
    expect(wrapper.find('textarea').element.value).toBe('updated')
  })
})
