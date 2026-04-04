import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import EKbd from '@/components/kbd/EKbd.vue'

describe('EKbd', () => {
  it('renders a kbd element with data-slot attribute', () => {
    const wrapper = mount(EKbd)
    expect(wrapper.find('kbd').exists()).toBe(true)
    expect(wrapper.find('[data-slot="kbd"]').exists()).toBe(true)
  })

  it('applies default kbd classes', () => {
    const wrapper = mount(EKbd)
    expect(wrapper.classes()).toContain('bg-muted')
    expect(wrapper.classes()).toContain('text-xs')
    expect(wrapper.classes()).toContain('rounded-sm')
  })

  it('renders slot content as text', () => {
    const wrapper = mount(EKbd, { slots: { default: 'Ctrl' } })
    expect(wrapper.text()).toBe('Ctrl')
  })

  it('renders slot content with HTML', () => {
    const wrapper = mount(EKbd, {
      slots: { default: '<span class="key">⌘</span>' },
    })
    expect(wrapper.find('.key').exists()).toBe(true)
    expect(wrapper.text()).toBe('⌘')
  })

  it('merges custom class with default classes', () => {
    const wrapper = mount(EKbd, { props: { class: 'my-kbd-class' } })
    expect(wrapper.classes()).toContain('my-kbd-class')
    expect(wrapper.classes()).toContain('bg-muted')
  })
})
