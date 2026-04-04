import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import ESpinner from '@/components/spinner/ESpinner.vue'

describe('ESpinner', () => {
  it('renders an SVG element', () => {
    const wrapper = mount(ESpinner)
    expect(wrapper.find('svg').exists()).toBe(true)
  })

  it('has role="status" for accessibility', () => {
    const wrapper = mount(ESpinner)
    expect(wrapper.find('svg').attributes('role')).toBe('status')
  })

  it('has aria-label for accessibility', () => {
    const wrapper = mount(ESpinner)
    expect(wrapper.find('svg').attributes('aria-label')).toBe('Loading')
  })

  it('applies animate-spin class', () => {
    const wrapper = mount(ESpinner)
    expect(wrapper.find('svg').classes()).toContain('animate-spin')
  })

  it('applies default size class (size-4)', () => {
    const wrapper = mount(ESpinner)
    expect(wrapper.find('svg').classes()).toContain('size-4')
  })

  it('applies sm size class (size-3)', () => {
    const wrapper = mount(ESpinner, { props: { size: 'sm' } })
    expect(wrapper.find('svg').classes()).toContain('size-3')
  })

  it('applies lg size class (size-6)', () => {
    const wrapper = mount(ESpinner, { props: { size: 'lg' } })
    expect(wrapper.find('svg').classes()).toContain('size-6')
  })

  it('merges custom class', () => {
    const wrapper = mount(ESpinner, { props: { class: 'text-red-500' } })
    expect(wrapper.find('svg').classes()).toContain('text-red-500')
  })
})
