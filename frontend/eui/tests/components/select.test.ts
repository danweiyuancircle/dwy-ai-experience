import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import ESelect from '@/components/select/ESelect.vue'

describe('ESelect', () => {
  const options = [
    { label: 'Apple', value: 'apple' },
    { label: 'Banana', value: 'banana' },
    { label: 'Cherry', value: 'cherry' },
  ]

  it('renders the select trigger element', () => {
    const wrapper = mount(ESelect, { props: { options } })
    expect(wrapper.find('[data-slot="select-trigger"]').exists()).toBe(true)
  })

  it('renders with placeholder text', () => {
    const wrapper = mount(ESelect, {
      props: { options, placeholder: 'Please select' },
    })
    expect(wrapper.text()).toContain('Please select')
  })

  it('does not render dropdown content in closed state (portal)', () => {
    const wrapper = mount(ESelect, { props: { options } })
    expect(wrapper.find('[data-slot="select-content"]').exists()).toBe(false)
  })

  it('accepts options prop without error', () => {
    const wrapper = mount(ESelect, { props: { options } })
    expect(wrapper.find('[data-slot="select-trigger"]').exists()).toBe(true)
  })

  it('renders with empty options array', () => {
    const wrapper = mount(ESelect, { props: { options: [] } })
    expect(wrapper.find('[data-slot="select-trigger"]').exists()).toBe(true)
  })

  it('accepts disabled prop', () => {
    const wrapper = mount(ESelect, {
      props: { options, disabled: true },
    })
    const trigger = wrapper.find('[data-slot="select-trigger"]')
    expect(trigger.attributes('disabled')).toBeDefined()
  })

  it('accepts modelValue prop for single mode', () => {
    const wrapper = mount(ESelect, {
      props: { options, modelValue: 'apple' },
    })
    expect(wrapper.find('[data-slot="select-trigger"]').exists()).toBe(true)
  })

  it('accepts multiple prop', () => {
    const wrapper = mount(ESelect, {
      props: { options, multiple: true, modelValue: ['apple'] },
    })
    expect(wrapper.find('[data-slot="select-trigger"]').exists()).toBe(true)
  })

  it('renders placeholder in multiple mode when no selection', () => {
    const wrapper = mount(ESelect, {
      props: { options, multiple: true, modelValue: [], placeholder: 'Choose items' },
    })
    expect(wrapper.text()).toContain('Choose items')
  })

  it('accepts size prop', () => {
    const wrapper = mount(ESelect, {
      props: { options, size: 'sm' },
    })
    const trigger = wrapper.find('[data-slot="select-trigger"]')
    expect(trigger.classes()).toContain('text-xs')
  })
})
