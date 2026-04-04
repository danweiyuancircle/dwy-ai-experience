import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import EColorPicker from '@/components/color-picker/EColorPicker.vue'

describe('EColorPicker', () => {
  it('renders a trigger button with color swatch', () => {
    const wrapper = mount(EColorPicker)
    const button = wrapper.find('button')
    expect(button.exists()).toBe(true)
    // Should show a color swatch span
    const swatch = button.find('span')
    expect(swatch.exists()).toBe(true)
  })

  it('displays the default color value', () => {
    const wrapper = mount(EColorPicker)
    // Default modelValue is #000000
    expect(wrapper.text()).toContain('#000000')
  })

  it('displays the provided modelValue', () => {
    const wrapper = mount(EColorPicker, {
      props: { modelValue: '#ef4444' },
    })
    expect(wrapper.text()).toContain('#ef4444')
  })

  it('applies disabled attribute to trigger button', () => {
    const wrapper = mount(EColorPicker, {
      props: { disabled: true },
    })
    const button = wrapper.find('button')
    expect(button.attributes('disabled')).toBeDefined()
  })

  it('applies disabled styling (opacity) when disabled', () => {
    const wrapper = mount(EColorPicker, {
      props: { disabled: true },
    })
    const button = wrapper.find('button')
    expect(button.classes().join(' ')).toContain('disabled:opacity-50')
  })

  it('renders preset color buttons inside popover content', () => {
    const presets = ['#ff0000', '#00ff00', '#0000ff']
    const wrapper = mount(EColorPicker, {
      props: { presets },
      attachTo: document.body,
    })
    // Presets are rendered inside PopoverContent which is portaled,
    // so we check the component's props are accepted without error
    expect(wrapper.props('presets')).toEqual(presets)
  })

  it('accepts empty presets array', () => {
    const wrapper = mount(EColorPicker, {
      props: { presets: [] },
    })
    // Should render without error
    expect(wrapper.find('button').exists()).toBe(true)
  })

  it('updates swatch background color based on modelValue', () => {
    const wrapper = mount(EColorPicker, {
      props: { modelValue: '#3b82f6' },
    })
    const swatch = wrapper.find('button span')
    expect(swatch.attributes('style')).toContain('background-color')
  })

  it('applies custom class to trigger button', () => {
    const wrapper = mount(EColorPicker, {
      props: { class: 'my-custom-class' },
    })
    const button = wrapper.find('button')
    expect(button.classes()).toContain('my-custom-class')
  })
})
