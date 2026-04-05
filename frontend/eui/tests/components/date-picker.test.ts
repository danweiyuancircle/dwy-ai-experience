import { mount } from '@vue/test-utils'
import { describe, it, expect, vi } from 'vitest'
import { nextTick } from 'vue'
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

  it('month picker renders month cells without errors', async () => {
    const spy = vi.spyOn(console, 'warn').mockImplementation(() => {})
    const errorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})

    const wrapper = mount(EDatePicker, {
      props: { type: 'month', modelValue: '2025-03' },
      attachTo: document.body,
    })

    // Open popover
    await wrapper.find('button').trigger('click')
    await nextTick()
    await nextTick()

    // Month picker cells should render with [data-reka-month-picker-cell-trigger] attribute
    const cellTriggers = document.querySelectorAll('[data-reka-month-picker-cell-trigger]')
    expect(cellTriggers.length).toBeGreaterThan(0)

    // Click a month cell — should emit update:modelValue
    const firstCell = cellTriggers[0] as HTMLElement
    firstCell.click()
    await nextTick()
    await nextTick()

    const emitted = wrapper.emitted('update:modelValue')
    expect(emitted).toBeTruthy()
    expect(emitted![0][0]).toMatch(/^\d{4}-\d{2}$/)

    spy.mockRestore()
    errorSpy.mockRestore()
    wrapper.unmount()
  })

  it('year picker renders year cells without errors', async () => {
    const spy = vi.spyOn(console, 'warn').mockImplementation(() => {})
    const errorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})

    const wrapper = mount(EDatePicker, {
      props: { type: 'year', modelValue: '2025' },
      attachTo: document.body,
    })

    // Open popover
    await wrapper.find('button').trigger('click')
    await nextTick()
    await nextTick()

    // Year picker cells should render with [data-reka-year-picker-cell-trigger] attribute
    const cellTriggers = document.querySelectorAll('[data-reka-year-picker-cell-trigger]')
    expect(cellTriggers.length).toBeGreaterThan(0)

    // Click a year cell — should emit update:modelValue
    const firstCell = cellTriggers[0] as HTMLElement
    firstCell.click()
    await nextTick()
    await nextTick()

    const emitted = wrapper.emitted('update:modelValue')
    expect(emitted).toBeTruthy()
    expect(emitted![0][0]).toMatch(/^\d{4}$/)

    spy.mockRestore()
    errorSpy.mockRestore()
    wrapper.unmount()
  })
})
