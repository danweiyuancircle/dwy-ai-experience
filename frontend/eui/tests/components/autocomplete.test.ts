import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import EAutocomplete from '@/components/autocomplete/EAutocomplete.vue'

describe('EAutocomplete', () => {
  it('renders an input element by default', () => {
    const wrapper = mount(EAutocomplete)
    expect(wrapper.find('input').exists()).toBe(true)
  })

  it('displays placeholder text', () => {
    const wrapper = mount(EAutocomplete, {
      props: { placeholder: 'Search here' },
    })
    expect(wrapper.find('input').attributes('placeholder')).toBe('Search here')
  })

  it('binds modelValue to input value', () => {
    const wrapper = mount(EAutocomplete, {
      props: { modelValue: 'hello' },
    })
    expect(wrapper.find('input').element.value).toBe('hello')
  })

  it('disables input when disabled prop is true', () => {
    const wrapper = mount(EAutocomplete, {
      props: { disabled: true },
    })
    expect(wrapper.find('input').attributes('disabled')).toBeDefined()
  })

  it('does not show suggestions dropdown initially', () => {
    const wrapper = mount(EAutocomplete)
    expect(wrapper.find('ul').exists()).toBe(false)
  })

  // Security: DOM value hiding
  it('does not expose value as HTML attribute', () => {
    const wrapper = mount(EAutocomplete, { props: { modelValue: 'secret' } })
    const input = wrapper.find('input')
    expect(input.attributes('value')).toBeUndefined()
    expect(input.element.value).toBe('secret')
  })
})
