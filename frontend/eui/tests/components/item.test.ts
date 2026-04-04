import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import EItem from '@/components/item/EItem.vue'

describe('EItem', () => {
  it('renders with default props', () => {
    const wrapper = mount(EItem)
    expect(wrapper.element.tagName).toBe('DIV')
    expect(wrapper.attributes('data-slot')).toBe('item')
  })

  it('renders slot content', () => {
    const wrapper = mount(EItem, { slots: { default: 'Item content' } })
    expect(wrapper.text()).toContain('Item content')
  })

  it('applies default variant class', () => {
    const wrapper = mount(EItem)
    expect(wrapper.classes()).toContain('bg-transparent')
  })

  it('applies outline variant class', () => {
    const wrapper = mount(EItem, { props: { variant: 'outline' } })
    expect(wrapper.classes()).toContain('border-border')
  })

  it('applies muted variant class', () => {
    const wrapper = mount(EItem, { props: { variant: 'muted' } })
    expect(wrapper.classes()).toContain('bg-muted/50')
  })

  it('applies default size class', () => {
    const wrapper = mount(EItem)
    expect(wrapper.classes()).toContain('p-4')
    expect(wrapper.classes()).toContain('gap-4')
  })

  it('applies sm size class', () => {
    const wrapper = mount(EItem, { props: { size: 'sm' } })
    expect(wrapper.classes()).toContain('py-3')
    expect(wrapper.classes()).toContain('px-4')
    expect(wrapper.classes()).toContain('gap-2.5')
  })

  it('renders as custom element via as prop', () => {
    const wrapper = mount(EItem, { props: { as: 'section' } })
    expect(wrapper.element.tagName).toBe('SECTION')
  })

  it('merges custom class', () => {
    const wrapper = mount(EItem, { props: { class: 'my-custom' } })
    expect(wrapper.classes()).toContain('my-custom')
  })
})
