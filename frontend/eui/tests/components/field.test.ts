import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import EField from '@/components/field/EField.vue'

describe('EField', () => {
  it('renders with default props', () => {
    const wrapper = mount(EField)
    expect(wrapper.element.tagName).toBe('DIV')
    expect(wrapper.attributes('data-slot')).toBe('field')
    expect(wrapper.attributes('role')).toBe('group')
  })

  it('renders slot content', () => {
    const wrapper = mount(EField, { slots: { default: '<input placeholder="test" />' } })
    expect(wrapper.find('input').exists()).toBe(true)
  })

  it('defaults to vertical orientation', () => {
    const wrapper = mount(EField)
    expect(wrapper.attributes('data-orientation')).toBe('vertical')
    expect(wrapper.classes()).toContain('flex-col')
  })

  it('applies horizontal orientation', () => {
    const wrapper = mount(EField, { props: { orientation: 'horizontal' } })
    expect(wrapper.attributes('data-orientation')).toBe('horizontal')
    expect(wrapper.classes()).toContain('flex-row')
  })

  it('applies responsive orientation', () => {
    const wrapper = mount(EField, { props: { orientation: 'responsive' } })
    expect(wrapper.attributes('data-orientation')).toBe('responsive')
    expect(wrapper.classes()).toContain('flex-col')
  })

  it('sets data-invalid attribute when invalid', () => {
    const wrapper = mount(EField, { props: { invalid: true } })
    expect(wrapper.attributes('data-invalid')).toBe('true')
  })

  it('does not set data-invalid when not invalid', () => {
    const wrapper = mount(EField)
    expect(wrapper.attributes('data-invalid')).toBe('false')
  })

  it('merges custom class', () => {
    const wrapper = mount(EField, { props: { class: 'my-field' } })
    expect(wrapper.classes()).toContain('my-field')
  })
})
