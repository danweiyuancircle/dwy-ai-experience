import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import ECombobox from '@/components/combobox/ECombobox.vue'

describe('ECombobox', () => {
  const options = [
    { label: 'React', value: 'react' },
    { label: 'Vue', value: 'vue' },
    { label: 'Angular', value: 'angular' },
  ]

  it('renders without error', () => {
    const wrapper = mount(ECombobox, { props: { options } })
    expect(wrapper.exists()).toBe(true)
  })

  it('renders the combobox input with placeholder', () => {
    const wrapper = mount(ECombobox, {
      props: { options, placeholder: 'Pick a framework' },
    })
    const input = wrapper.find('input')
    expect(input.exists()).toBe(true)
    expect(input.attributes('placeholder')).toBe('Pick a framework')
  })

  it('uses default placeholder when not provided', () => {
    const wrapper = mount(ECombobox, { props: { options } })
    const input = wrapper.find('input')
    expect(input.attributes('placeholder')).toBe('Select an option...')
  })

  it('accepts options prop without error', () => {
    const wrapper = mount(ECombobox, { props: { options } })
    expect(wrapper.find('input').exists()).toBe(true)
  })

  it('renders with empty options array', () => {
    const wrapper = mount(ECombobox, { props: { options: [] } })
    expect(wrapper.find('input').exists()).toBe(true)
  })

  it('accepts disabled prop', () => {
    const wrapper = mount(ECombobox, {
      props: { options, disabled: true },
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('accepts modelValue prop', () => {
    const wrapper = mount(ECombobox, {
      props: { options, modelValue: 'vue' },
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('accepts emptyText prop', () => {
    const wrapper = mount(ECombobox, {
      props: { options: [], emptyText: 'Nothing here' },
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('does not render dropdown content in closed state (portal)', () => {
    const wrapper = mount(ECombobox, { props: { options } })
    // Dropdown content is portaled outside the wrapper
    expect(wrapper.find('[data-slot="combobox-content"]').exists()).toBe(false)
  })
})
