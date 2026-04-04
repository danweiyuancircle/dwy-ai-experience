import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import ESeparator from '@/components/separator/ESeparator.vue'

describe('ESeparator', () => {
  it('renders with data-slot attribute', () => {
    const wrapper = mount(ESeparator)
    expect(wrapper.attributes('data-slot')).toBe('separator')
  })

  it('defaults to horizontal orientation', () => {
    const wrapper = mount(ESeparator)
    expect(wrapper.attributes('data-orientation')).toBe('horizontal')
  })

  it('applies horizontal orientation classes', () => {
    const wrapper = mount(ESeparator, { props: { orientation: 'horizontal' } })
    expect(wrapper.attributes('data-orientation')).toBe('horizontal')
    expect(wrapper.classes()).toContain('bg-border')
    expect(wrapper.classes()).toContain('shrink-0')
  })

  it('applies vertical orientation', () => {
    const wrapper = mount(ESeparator, { props: { orientation: 'vertical' } })
    expect(wrapper.attributes('data-orientation')).toBe('vertical')
  })

  it('applies decorative role by default', () => {
    const wrapper = mount(ESeparator)
    expect(wrapper.attributes('role')).toBe('none')
  })

  it('applies separator role when not decorative', () => {
    const wrapper = mount(ESeparator, { props: { decorative: false } })
    expect(wrapper.attributes('role')).toBe('separator')
  })

  it('merges custom class', () => {
    const wrapper = mount(ESeparator, { props: { class: 'my-separator' } })
    expect(wrapper.classes()).toContain('my-separator')
  })
})
