import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import EDatePicker from '@/components/date-picker/EDatePicker.vue'

describe('EDatePicker', () => {
  it('renders a trigger button', () => {
    const wrapper = mount(EDatePicker)
    expect(wrapper.find('button').exists()).toBe(true)
  })

  it('displays placeholder when no value is set', () => {
    const wrapper = mount(EDatePicker, {
      props: { placeholder: 'Select date' },
    })
    expect(wrapper.text()).toContain('Select date')
  })

  it('shows default placeholder text', () => {
    const wrapper = mount(EDatePicker)
    expect(wrapper.text()).toContain('Pick a date')
  })

  it('disables trigger when disabled prop is true', () => {
    const wrapper = mount(EDatePicker, {
      props: { disabled: true },
    })
    expect(wrapper.find('button').attributes('disabled')).toBeDefined()
  })

  it('renders calendar icon', () => {
    const wrapper = mount(EDatePicker)
    expect(wrapper.find('svg').exists()).toBe(true)
  })
})
