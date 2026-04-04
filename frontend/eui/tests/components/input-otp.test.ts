import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import EInputOTP from '@/components/input-otp/EInputOTP.vue'

describe('EInputOTP', () => {
  it('renders with data-slot attribute', () => {
    const wrapper = mount(EInputOTP)
    expect(wrapper.find('[data-slot="input-otp"]').exists()).toBe(true)
  })

  it('renders 6 input slots by default', () => {
    const wrapper = mount(EInputOTP)
    const slots = wrapper.findAll('[data-slot="input-otp-slot"]')
    expect(slots).toHaveLength(6)
  })

  it('renders custom number of slots via length prop', () => {
    const wrapper = mount(EInputOTP, { props: { length: 4 } })
    const slots = wrapper.findAll('[data-slot="input-otp-slot"]')
    expect(slots).toHaveLength(4)
  })

  it('applies disabled state', () => {
    const wrapper = mount(EInputOTP, { props: { disabled: true } })
    const root = wrapper.find('[data-slot="input-otp"]')
    expect(root.attributes('data-disabled')).toBeDefined()
  })

  it('applies placeholder to input slots', () => {
    const wrapper = mount(EInputOTP, { props: { placeholder: '0' } })
    const slots = wrapper.findAll('[data-slot="input-otp-slot"]')
    expect(slots[0].attributes('placeholder')).toBe('0')
  })

  it('has input-otp-group wrapper', () => {
    const wrapper = mount(EInputOTP)
    expect(wrapper.find('[data-slot="input-otp-group"]').exists()).toBe(true)
  })
})
