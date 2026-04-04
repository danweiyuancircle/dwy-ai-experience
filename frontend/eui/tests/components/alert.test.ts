import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import EAlert from '@/components/alert/EAlert.vue'

describe('EAlert', () => {
  it('renders with role="alert"', () => {
    const wrapper = mount(EAlert)
    expect(wrapper.attributes('role')).toBe('alert')
  })

  it('renders title prop', () => {
    const wrapper = mount(EAlert, { props: { title: '标题' } })
    expect(wrapper.find('[data-slot="alert-title"]').text()).toBe('标题')
  })

  it('renders description prop', () => {
    const wrapper = mount(EAlert, { props: { description: '详细内容' } })
    expect(wrapper.find('[data-slot="alert-description"]').text()).toBe('详细内容')
  })

  it('renders default slot as description', () => {
    const wrapper = mount(EAlert, { slots: { default: '自定义内容' } })
    expect(wrapper.find('[data-slot="alert-description"]').text()).toBe('自定义内容')
  })

  it('renders title slot', () => {
    const wrapper = mount(EAlert, { slots: { title: '自定义标题' } })
    expect(wrapper.find('[data-slot="alert-title"]').text()).toBe('自定义标题')
  })

  it('applies default variant class', () => {
    const wrapper = mount(EAlert)
    expect(wrapper.classes()).toContain('bg-card')
  })

  it('applies destructive variant class', () => {
    const wrapper = mount(EAlert, { props: { variant: 'destructive' } })
    expect(wrapper.classes()).toContain('text-destructive')
  })

  it('hides close button by default', () => {
    const wrapper = mount(EAlert)
    expect(wrapper.find('button').exists()).toBe(false)
  })

  it('shows close button when closable', () => {
    const wrapper = mount(EAlert, { props: { closable: true } })
    const btn = wrapper.find('button')
    expect(btn.exists()).toBe(true)
    expect(btn.attributes('aria-label')).toBe('Close alert')
  })

  it('emits close event on close button click', async () => {
    const wrapper = mount(EAlert, { props: { closable: true } })
    await wrapper.find('button').trigger('click')
    expect(wrapper.emitted('close')).toHaveLength(1)
  })

  it('merges custom class', () => {
    const wrapper = mount(EAlert, { props: { class: 'my-alert' } })
    expect(wrapper.classes()).toContain('my-alert')
  })

  it('has data-slot attribute', () => {
    const wrapper = mount(EAlert)
    expect(wrapper.attributes('data-slot')).toBe('alert')
  })

  it('hides title section when no title', () => {
    const wrapper = mount(EAlert, { props: { description: 'only desc' } })
    expect(wrapper.find('[data-slot="alert-title"]').exists()).toBe(false)
  })

  it('hides description section when no description or slot', () => {
    const wrapper = mount(EAlert, { props: { title: 'only title' } })
    expect(wrapper.find('[data-slot="alert-description"]').exists()).toBe(false)
  })
})
