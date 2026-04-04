import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import ELabel from '@/components/label/ELabel.vue'

describe('ELabel', () => {
  it('renders a label element with data-slot attribute', () => {
    const wrapper = mount(ELabel)
    expect(wrapper.find('[data-slot="label"]').exists()).toBe(true)
  })

  it('renders as a label element', () => {
    const wrapper = mount(ELabel)
    expect(wrapper.find('label').exists()).toBe(true)
  })

  it('applies default label classes', () => {
    const wrapper = mount(ELabel)
    const label = wrapper.find('[data-slot="label"]')
    expect(label.classes()).toContain('flex')
    expect(label.classes()).toContain('text-sm')
    expect(label.classes()).toContain('font-medium')
  })

  it('sets for attribute when for prop is provided', () => {
    const wrapper = mount(ELabel, { props: { for: 'username-input' } })
    const label = wrapper.find('label')
    expect(label.attributes('for')).toBe('username-input')
  })

  it('does not set for attribute when for prop is not provided', () => {
    const wrapper = mount(ELabel)
    const label = wrapper.find('label')
    expect(label.attributes('for')).toBeUndefined()
  })

  it('renders slot content', () => {
    const wrapper = mount(ELabel, { slots: { default: '用户名' } })
    expect(wrapper.text()).toBe('用户名')
  })

  it('renders slot content with HTML', () => {
    const wrapper = mount(ELabel, {
      slots: { default: '<span>必填</span> 用户名' },
    })
    expect(wrapper.text()).toContain('必填')
    expect(wrapper.text()).toContain('用户名')
  })

  it('merges custom class with default classes', () => {
    const wrapper = mount(ELabel, { props: { class: 'my-label-class' } })
    const label = wrapper.find('[data-slot="label"]')
    expect(label.classes()).toContain('my-label-class')
    expect(label.classes()).toContain('text-sm')
  })
})
