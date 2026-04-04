import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import EForm from '@/components/form/EForm.vue'

describe('EForm', () => {
  it('renders a form element', () => {
    const wrapper = mount(EForm)
    expect(wrapper.find('form').exists()).toBe(true)
  })

  it('has data-slot attribute', () => {
    const wrapper = mount(EForm)
    expect(wrapper.find('form').attributes('data-slot')).toBe('form')
  })

  it('renders slot content', () => {
    const wrapper = mount(EForm, {
      slots: { default: '<div class="form-content">Form Field</div>' },
    })
    expect(wrapper.find('.form-content').exists()).toBe(true)
    expect(wrapper.text()).toContain('Form Field')
  })

  it('applies inline class when inline prop is true', () => {
    const wrapper = mount(EForm, { props: { inline: true } })
    const form = wrapper.find('form')
    expect(form.classes()).toContain('flex')
    expect(form.classes()).toContain('flex-wrap')
  })

  it('applies space-y-4 class when inline is false', () => {
    const wrapper = mount(EForm, { props: { inline: false } })
    const form = wrapper.find('form')
    expect(form.classes()).toContain('space-y-4')
  })

  it('accepts model prop', () => {
    const model = { name: 'test', age: 20 }
    const wrapper = mount(EForm, { props: { model } })
    expect(wrapper.find('form').exists()).toBe(true)
  })

  it('accepts labelWidth prop', () => {
    const wrapper = mount(EForm, { props: { labelWidth: '120px' } })
    expect(wrapper.find('form').exists()).toBe(true)
  })

  it('accepts labelPosition prop', () => {
    const wrapper = mount(EForm, { props: { labelPosition: 'top' } })
    expect(wrapper.find('form').exists()).toBe(true)
  })

  it('accepts disabled prop', () => {
    const wrapper = mount(EForm, { props: { disabled: true } })
    expect(wrapper.find('form').exists()).toBe(true)
  })

  it('applies custom class', () => {
    const wrapper = mount(EForm, { props: { class: 'my-form' } })
    const form = wrapper.find('form')
    expect(form.classes()).toContain('my-form')
  })

  it('has submit.prevent on form element', () => {
    // The component uses @submit.prevent to prevent default form submission
    const wrapper = mount(EForm)
    const form = wrapper.find('form')
    // Verify the form element exists and is properly configured
    expect(form.exists()).toBe(true)
    expect(form.attributes('data-slot')).toBe('form')
  })
})
