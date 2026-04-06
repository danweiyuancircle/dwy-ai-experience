import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import ETimePicker from '@/components/time-picker/ETimePicker.vue'

describe('ETimePicker', () => {
  it('renders a trigger button', () => {
    const wrapper = mount(ETimePicker)
    expect(wrapper.find('button').exists()).toBe(true)
  })

  it('displays placeholder when no value is set', () => {
    const wrapper = mount(ETimePicker, {
      props: { placeholder: 'Choose time' },
    })
    expect(wrapper.text()).toContain('Choose time')
  })

  it('shows default placeholder text', () => {
    const wrapper = mount(ETimePicker)
    expect(wrapper.text()).toContain('请选择时间')
  })

  it('displays modelValue when provided', () => {
    const wrapper = mount(ETimePicker, {
      props: { modelValue: '14:30' },
    })
    expect(wrapper.text()).toContain('14:30')
  })

  it('disables trigger when disabled prop is true', () => {
    const wrapper = mount(ETimePicker, {
      props: { disabled: true },
    })
    expect(wrapper.find('button').attributes('disabled')).toBeDefined()
  })
})
