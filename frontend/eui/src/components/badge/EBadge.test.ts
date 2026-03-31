import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import EBadge from './EBadge.vue'

describe('EBadge', () => {
  it('renders slot content', () => {
    const wrapper = mount(EBadge, { slots: { default: 'New' } })
    expect(wrapper.text()).toContain('New')
  })

  it('applies default variant class', () => {
    const wrapper = mount(EBadge)
    expect(wrapper.classes()).toContain('bg-primary')
  })

  it('applies secondary variant class', () => {
    const wrapper = mount(EBadge, { props: { variant: 'secondary' } })
    expect(wrapper.classes()).toContain('bg-secondary')
  })

  it('applies destructive variant class', () => {
    const wrapper = mount(EBadge, { props: { variant: 'destructive' } })
    expect(wrapper.classes()).toContain('bg-destructive')
  })

  it('applies outline variant class', () => {
    const wrapper = mount(EBadge, { props: { variant: 'outline' } })
    expect(wrapper.classes()).toContain('text-foreground')
  })

  it('merges custom class', () => {
    const wrapper = mount(EBadge, { props: { class: 'my-class' } })
    expect(wrapper.classes()).toContain('my-class')
  })

  it('renders as div by default (Primitive default)', () => {
    const wrapper = mount(EBadge)
    expect(wrapper.element.tagName).toBe('DIV')
  })

  it('has data-slot attribute', () => {
    const wrapper = mount(EBadge)
    expect(wrapper.attributes('data-slot')).toBe('badge')
  })
})
