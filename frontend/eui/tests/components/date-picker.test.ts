import { enableAutoUnmount, mount } from '@vue/test-utils'
import { afterEach, describe, it, expect, vi } from 'vitest'
import { h, nextTick, reactive, ref } from 'vue'
import EDatePicker from '@/components/date-picker/EDatePicker.vue'
import EConfigProvider from '@/components/config-provider/EConfigProvider.vue'

enableAutoUnmount(afterEach)

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

  it.each([
    ['date', '请选择日期'],
    ['month', '请选择日期'],
    ['year', '请选择日期'],
    ['daterange', '开始日期 至 结束日期'],
  ] as const)('%s uses Chinese defaults without a provider', (type, expected) => {
    const wrapper = mount(EDatePicker, { props: { type } })
    expect(wrapper.get('button').text()).toBe(expected)
  })

  it.each([
    ['date', '请选择日期'],
    ['month', '请选择日期'],
    ['year', '请选择日期'],
    ['daterange', '开始日期 至 结束日期'],
  ] as const)('%s uses the default provider locale', (type, expected) => {
    const wrapper = mount(EConfigProvider, {
      slots: { default: () => h(EDatePicker, { type }) },
    })
    expect(wrapper.get('button').text()).toBe(expected)
  })

  it.each([
    ['date', 'Choose date'],
    ['month', 'Choose date'],
    ['year', 'Choose date'],
    ['daterange', 'From to Until'],
  ] as const)('%s reads the provider text overrides', (type, expected) => {
    const wrapper = mount(EConfigProvider, {
      props: {
        locale: {
          name: 'en-US',
          datePickerPlaceholder: 'Choose date',
          datePickerStartPlaceholder: 'From',
          datePickerEndPlaceholder: 'Until',
          datePickerRangeSeparator: 'to',
        },
      },
      slots: { default: () => h(EDatePicker, { type }) },
    })
    expect(wrapper.get('button').text()).toBe(expected)
  })

  it('updates mounted pickers when provider text changes and merges partial overrides', async () => {
    const wrapper = mount(EConfigProvider, {
      slots: { default: () => [h(EDatePicker), h(EDatePicker, { type: 'daterange' })] },
    })
    await wrapper.setProps({ locale: { datePickerPlaceholder: 'Pick', datePickerStartPlaceholder: 'From' } })
    expect(wrapper.findAll('button').map(button => button.text())).toEqual(['Pick', 'From 至 结束日期'])

    await wrapper.setProps({ locale: { datePickerEndPlaceholder: 'Until', datePickerRangeSeparator: 'to' } })
    expect(wrapper.findAll('button').map(button => button.text())).toEqual(['请选择日期', '开始日期 to Until'])
  })

  it.each(['date', 'month', 'year'] as const)('%s preserves explicit placeholder including an empty string', async type => {
    const placeholder = ref('Custom date')
    const wrapper = mount(EConfigProvider, {
      props: { locale: { datePickerPlaceholder: 'Provider date' } },
      slots: { default: () => h(EDatePicker, { type, placeholder: placeholder.value }) },
    })
    expect(wrapper.get('button').text()).toBe('Custom date')
    placeholder.value = ''
    await nextTick()
    expect(wrapper.get('button').text()).toBe('')
  })

  it('preserves explicit range placeholders and separator including empty strings', async () => {
    const labels = reactive({ startPlaceholder: 'Custom start', endPlaceholder: 'Custom end', rangeSeparator: '/' })
    const wrapper = mount(EConfigProvider, {
      props: { locale: { datePickerStartPlaceholder: 'Provider start', datePickerEndPlaceholder: 'Provider end', datePickerRangeSeparator: 'to' } },
      slots: { default: () => h(EDatePicker, { type: 'daterange', ...labels }) },
    })
    expect(wrapper.get('button').text()).toBe('Custom start / Custom end')
    Object.assign(labels, { startPlaceholder: '', endPlaceholder: '', rangeSeparator: '' })
    await nextTick()
    expect(wrapper.get('button').text()).toBe('')
  })

  it.each([
    ['date', '2026-10-18', '2026-10-18', '请选择日期'],
    ['month', '2026-10', '2026-10', '请选择日期'],
    ['year', '2026', '2026', '请选择日期'],
    ['daterange', ['2026-10-18', '2026-10-20'], '2026-10-18 至 2026-10-20', '开始日期 至 结束日期'],
  ] as const)('%s returns to localized text after clearing a selected value', async (type, value, selected, empty) => {
    const wrapper = mount(EDatePicker, {
      props: { type, modelValue: value as string | [string, string], clearable: true },
    })
    expect(wrapper.get('button').text()).toBe(selected)
    await wrapper.get('svg.lucide-x').trigger('click')
    expect(wrapper.emitted('update:modelValue')).toEqual([[undefined]])
    expect(wrapper.emitted('change')).toEqual([[undefined]])
    await wrapper.setProps({ modelValue: undefined })
    expect(wrapper.get('button').text()).toBe(empty)
  })

  it('uses the localized separator for selected ranges and preserves explicit separator priority', async () => {
    const rangeSeparator = ref<string>()
    const wrapper = mount(EConfigProvider, {
      props: { locale: { datePickerRangeSeparator: 'to' } },
      slots: { default: () => h(EDatePicker, { type: 'daterange', modelValue: ['2026-10-18', '2026-10-20'], rangeSeparator: rangeSeparator.value }) },
    })
    expect(wrapper.get('button').text()).toBe('2026-10-18 to 2026-10-20')
    rangeSeparator.value = '/'
    await nextTick()
    expect(wrapper.get('button').text()).toBe('2026-10-18 / 2026-10-20')
  })

  it('selects a calendar day and returns to provider text after clearing', async () => {
    const value = ref<string>()
    const wrapper = mount(EConfigProvider, {
      props: { locale: { datePickerPlaceholder: '选择交易日' } },
      slots: {
        default: () => h(EDatePicker, {
          modelValue: value.value,
          clearable: true,
          'onUpdate:modelValue': next => { value.value = next as string | undefined },
        }),
      },
      attachTo: document.body,
    })
    const picker = wrapper.getComponent(EDatePicker)
    await wrapper.get('button').trigger('click')
    await nextTick()
    // 从当前日历读取日期，断言保持 ISO 值契约，不依赖测试运行日期。
    const cell = document.querySelector<HTMLElement>('[data-reka-calendar-cell-trigger]:not([data-outside-view])')!
    const selected = cell.getAttribute('data-value')!
    cell.click()
    await nextTick()
    expect(picker.emitted('update:modelValue')).toEqual([[selected]])
    expect(picker.emitted('change')).toEqual([[selected]])
    expect(wrapper.get('button').text()).toBe(selected)
    await wrapper.get('svg.lucide-x').trigger('click')
    expect(wrapper.get('button').text()).toBe('选择交易日')
    expect(picker.emitted('update:modelValue')).toEqual([[selected], [undefined]])
  })

  it('selects a complete date range and returns to provider text after clearing', async () => {
    const value = ref<[string, string]>()
    const wrapper = mount(EConfigProvider, {
      props: { locale: { datePickerStartPlaceholder: '起始', datePickerEndPlaceholder: '截止', datePickerRangeSeparator: '~' } },
      slots: {
        default: () => h(EDatePicker, {
          type: 'daterange',
          modelValue: value.value,
          clearable: true,
          'onUpdate:modelValue': next => { value.value = next as [string, string] | undefined },
        }),
      },
      attachTo: document.body,
    })
    const picker = wrapper.getComponent(EDatePicker)
    await wrapper.get('button').trigger('click')
    await nextTick()
    const cells = document.querySelectorAll<HTMLElement>('[data-reka-calendar-cell-trigger]:not([data-outside-view])')
    const start = cells[0]!.getAttribute('data-value')!
    const end = cells[1]!.getAttribute('data-value')!
    cells[0]!.click()
    await nextTick()
    await nextTick()
    expect(picker.emitted('update:modelValue')).toBeUndefined()
    const endCell = document.querySelector<HTMLElement>(`[data-value="${end}"]:not([data-outside-view])`)!
    // 区间终点依赖悬停后的 highlightedRange，与真实指针操作保持一致。
    endCell.dispatchEvent(new MouseEvent('mouseenter'))
    await nextTick()
    endCell.click()
    await nextTick()
    await nextTick()
    expect(picker.emitted('update:modelValue')).toEqual([[[start, end]]])
    expect(picker.emitted('change')).toEqual([[[start, end]]])
    expect(wrapper.get('button').text()).toBe(`${start} ~ ${end}`)
    await wrapper.get('svg.lucide-x').trigger('click')
    expect(wrapper.get('button').text()).toBe('起始 ~ 截止')
    expect(picker.emitted('update:modelValue')).toEqual([[[start, end]], [undefined]])
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
