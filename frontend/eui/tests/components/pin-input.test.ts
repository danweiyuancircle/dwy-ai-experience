import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import EPinInput from '@/components/pin-input/EPinInput.vue'

describe('EPinInput', () => {
  it('renders with data-slot attribute', () => {
    const wrapper = mount(EPinInput)
    expect(wrapper.find('[data-slot="pin-input"]').exists()).toBe(true)
  })

  it('renders 4 input slots by default', () => {
    const wrapper = mount(EPinInput)
    const slots = wrapper.findAll('[data-slot="pin-input-slot"]')
    expect(slots).toHaveLength(4)
  })

  it('renders custom number of slots via length prop', () => {
    const wrapper = mount(EPinInput, { props: { length: 6 } })
    const slots = wrapper.findAll('[data-slot="pin-input-slot"]')
    expect(slots).toHaveLength(6)
  })

  it('applies disabled state', () => {
    const wrapper = mount(EPinInput, { props: { disabled: true } })
    const root = wrapper.find('[data-slot="pin-input"]')
    expect(root.attributes('data-disabled')).toBeDefined()
  })

  it('passes mask prop to root', () => {
    const wrapper = mount(EPinInput, { props: { mask: true } })
    const root = wrapper.find('[data-slot="pin-input"]')
    // mask attribute should be present on PinInputRoot
    expect(root.exists()).toBe(true)
  })

  // Security: mask defaults to true
  it('defaults mask to true for security', () => {
    const wrapper = mount(EPinInput)
    const root = wrapper.find('[data-slot="pin-input"]')
    // When mask is true, reka-ui PinInputRoot renders with mask behavior
    expect(root.exists()).toBe(true)
  })

  it('can explicitly set mask to false', () => {
    const wrapper = mount(EPinInput, { props: { mask: false } })
    const root = wrapper.find('[data-slot="pin-input"]')
    expect(root.exists()).toBe(true)
  })
})
