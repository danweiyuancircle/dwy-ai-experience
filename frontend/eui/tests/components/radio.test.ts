import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import ERadio from '@/components/radio/ERadio.vue'

const defaultOptions = [
  { label: '选项一', value: 'a' },
  { label: '选项二', value: 'b' },
  { label: '选项三', value: 'c' },
]

describe('ERadio', () => {
  it('renders a radio group with options', () => {
    const wrapper = mount(ERadio, {
      props: { options: defaultOptions },
    })
    expect(wrapper.find('[data-slot="radio-group"]').exists()).toBe(true)
    const items = wrapper.findAll('[data-slot="radio-group-item"]')
    expect(items.length).toBe(3)
  })

  it('renders option labels', () => {
    const wrapper = mount(ERadio, {
      props: { options: defaultOptions },
    })
    expect(wrapper.text()).toContain('选项一')
    expect(wrapper.text()).toContain('选项二')
    expect(wrapper.text()).toContain('选项三')
  })

  it('binds v-model and emits update on selection', async () => {
    const wrapper = mount(ERadio, {
      props: {
        options: defaultOptions,
        modelValue: 'a',
        'onUpdate:modelValue': (val: string) => wrapper.setProps({ modelValue: val }),
      },
    })
    // Click the second radio item
    const items = wrapper.findAll('[data-slot="radio-group-item"]')
    await items[1].trigger('click')
    const emitted = wrapper.emitted('update:modelValue')
    expect(emitted).toBeTruthy()
    expect(emitted![emitted!.length - 1][0]).toBe('b')
  })

  it('preserves number option value type on emit (not coerced to string)', async () => {
    const numberOptions = [
      { label: '一', value: 1 },
      { label: '二', value: 2 },
    ]
    const wrapper = mount(ERadio, {
      props: {
        options: numberOptions,
        modelValue: 1,
        'onUpdate:modelValue': (val: string | number) => wrapper.setProps({ modelValue: val }),
      },
    })
    const items = wrapper.findAll('[data-slot="radio-group-item"]')
    await items[1].trigger('click')
    const emitted = wrapper.emitted('update:modelValue')
    expect(emitted).toBeTruthy()
    expect(emitted![emitted!.length - 1][0]).toBe(2)
    expect(typeof emitted![emitted!.length - 1][0]).toBe('number')
  })

  it('disables all items when disabled prop is true', () => {
    const wrapper = mount(ERadio, {
      props: { options: defaultOptions, disabled: true },
    })
    // Each radio item should be disabled
    const items = wrapper.findAll('[data-slot="radio-group-item"]')
    items.forEach((item) => {
      expect(item.attributes('disabled')).toBeDefined()
    })
    // Wrapper labels should have disabled styling
    const labels = wrapper.findAll('label')
    labels.forEach((label) => {
      expect(label.classes()).toContain('cursor-not-allowed')
    })
  })

  it('disables individual option', () => {
    const options = [
      { label: '可用', value: 'a' },
      { label: '禁用', value: 'b', disabled: true },
    ]
    const wrapper = mount(ERadio, {
      props: { options },
    })
    const items = wrapper.findAll('[data-slot="radio-group-item"]')
    expect(items[0].attributes('disabled')).toBeUndefined()
    expect(items[1].attributes('disabled')).toBeDefined()
  })

  it('renders horizontal layout by default', () => {
    const wrapper = mount(ERadio, {
      props: { options: defaultOptions },
    })
    const group = wrapper.find('[data-slot="radio-group"]')
    expect(group.classes()).toContain('flex-row')
  })

  it('renders vertical layout when direction is vertical', () => {
    const wrapper = mount(ERadio, {
      props: { options: defaultOptions, direction: 'vertical' },
    })
    const group = wrapper.find('[data-slot="radio-group"]')
    expect(group.classes()).toContain('grid')
  })

  it('renders button mode when optionType is button', () => {
    const wrapper = mount(ERadio, {
      props: { options: defaultOptions, optionType: 'button' },
    })
    const buttonItems = wrapper.findAll('[data-slot="radio-button-item"]')
    expect(buttonItems.length).toBe(3)
    // No default radio items should exist
    expect(wrapper.findAll('[data-slot="radio-group-item"]').length).toBe(0)
  })

  it('applies inline-flex class in button mode', () => {
    const wrapper = mount(ERadio, {
      props: { options: defaultOptions, optionType: 'button' },
    })
    const group = wrapper.find('[data-slot="radio-group"]')
    expect(group.classes()).toContain('inline-flex')
  })

  it('applies size classes for sm size', () => {
    const wrapper = mount(ERadio, {
      props: { options: defaultOptions, size: 'sm' },
    })
    const items = wrapper.findAll('[data-slot="radio-group-item"]')
    // sm radio should have size-3.5 class
    expect(items[0].classes()).toContain('size-3.5')
  })
})
