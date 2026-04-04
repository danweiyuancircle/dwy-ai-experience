import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import ESkeleton from '@/components/skeleton/ESkeleton.vue'

describe('ESkeleton', () => {
  it('renders a div element', () => {
    const wrapper = mount(ESkeleton)
    expect(wrapper.element.tagName).toBe('DIV')
  })

  it('has data-slot attribute', () => {
    const wrapper = mount(ESkeleton)
    expect(wrapper.attributes('data-slot')).toBe('skeleton')
  })

  it('applies animate-pulse class for animation', () => {
    const wrapper = mount(ESkeleton)
    expect(wrapper.classes()).toContain('animate-pulse')
  })

  it('applies rounded-md class', () => {
    const wrapper = mount(ESkeleton)
    expect(wrapper.classes()).toContain('rounded-md')
  })

  it('applies background class', () => {
    const wrapper = mount(ESkeleton)
    expect(wrapper.classes()).toContain('bg-primary/10')
  })

  it('merges custom class', () => {
    const wrapper = mount(ESkeleton, { props: { class: 'h-4 w-full' } })
    expect(wrapper.classes()).toContain('h-4')
    expect(wrapper.classes()).toContain('w-full')
  })
})
