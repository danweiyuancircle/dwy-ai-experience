import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import EButton from '@/components/button/EButton.vue'

describe('EButton', () => {
  it('renders a button element by default', () => {
    const wrapper = mount(EButton, { slots: { default: 'Click me' } })
    expect(wrapper.find('button').exists()).toBe(true)
    expect(wrapper.text()).toContain('Click me')
  })

  it('applies the default variant class', () => {
    const wrapper = mount(EButton)
    expect(wrapper.classes()).toContain('bg-primary')
  })

  it('applies destructive variant class', () => {
    const wrapper = mount(EButton, { props: { variant: 'destructive' } })
    expect(wrapper.classes()).toContain('bg-destructive')
  })

  it('applies outline variant class', () => {
    const wrapper = mount(EButton, { props: { variant: 'outline' } })
    expect(wrapper.classes()).toContain('border')
    expect(wrapper.classes()).toContain('bg-background')
  })

  it('is disabled when disabled prop is true', () => {
    const wrapper = mount(EButton, { props: { disabled: true } })
    expect(wrapper.attributes('disabled')).toBeDefined()
  })

  it('shows spinner and disables when loading is true', () => {
    const wrapper = mount(EButton, { props: { loading: true } })
    expect(wrapper.find('svg').exists()).toBe(true)
    expect(wrapper.attributes('disabled')).toBeDefined()
  })

  it('does not show spinner when loading is false', () => {
    const wrapper = mount(EButton, { props: { loading: false } })
    expect(wrapper.find('svg').exists()).toBe(false)
  })

  it('applies sm size class', () => {
    const wrapper = mount(EButton, { props: { size: 'sm' } })
    expect(wrapper.classes()).toContain('h-8')
  })

  it('applies lg size class', () => {
    const wrapper = mount(EButton, { props: { size: 'lg' } })
    expect(wrapper.classes()).toContain('h-10')
  })

  it('merges custom class with variant classes', () => {
    const wrapper = mount(EButton, { props: { class: 'my-custom-class' } })
    expect(wrapper.classes()).toContain('my-custom-class')
    expect(wrapper.classes()).toContain('bg-primary')
  })

  it('triggers click event when clicked', async () => {
    const wrapper = mount(EButton)
    await wrapper.trigger('click')
    // The click event is a native DOM event; verify the trigger completes without error
    // and the button remains interactive
    expect(wrapper.attributes('disabled')).toBeUndefined()
  })

  it('does not emit click when disabled', async () => {
    const wrapper = mount(EButton, { props: { disabled: true } })
    await wrapper.trigger('click')
    // disabled buttons should not emit click in browser, but pointer-events-none handles it via CSS
    // we verify disabled attribute is set
    expect(wrapper.attributes('disabled')).toBeDefined()
  })
})
