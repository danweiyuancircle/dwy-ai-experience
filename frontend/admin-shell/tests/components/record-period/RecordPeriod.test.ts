/**
 * RecordPeriod：快捷档和完整区间才向外抛。日期框不撑满。
 */
import { defineComponent } from 'vue'
import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import { RecordPeriod } from '../../../src/components'

const EDatePicker = defineComponent({
  name: 'EDatePicker',
  props: {
    modelValue: { type: [String, Array], default: undefined },
    disabledDate: { type: Function, default: undefined },
    clearable: { type: Boolean, default: true },
  },
  emits: ['change', 'update:modelValue'],
  template: '<div class="date" />',
})

const EToggleGroup = defineComponent({
  name: 'EToggleGroup',
  props: { modelValue: String },
  template: '<div class="group"><slot /></div>',
})

const EToggleGroupItem = defineComponent({
  name: 'EToggleGroupItem',
  props: { value: String },
  template: '<span><slot /></span>',
})

describe('RecordPeriod', () => {
  function mountPeriod() {
    return mount(RecordPeriod, {
      props: {
        label: '账期',
        preset: 'this',
        presets: [
          { label: '本月', value: 'this' },
          { label: '上个月', value: 'last' },
        ],
        range: ['2026-10-01', '2026-10-14'],
      },
      global: { stubs: { EDatePicker, EToggleGroup, EToggleGroupItem } },
    })
  }

  it('日期框收成内容宽度，且不能清空', () => {
    const wrapper = mountPeriod()
    const picker = wrapper.getComponent({ name: 'EDatePicker' })

    expect(wrapper.text()).toContain('账期')
    expect(picker.attributes('class')).toContain('w-auto')
    expect(picker.props('clearable')).toBe(false)
  })

  it('点快捷档向外抛，半截区间不抛', async () => {
    const wrapper = mountPeriod()

    await wrapper.getComponent({ name: 'SegmentedFilter' }).vm.$emit('update:modelValue', 'last')
    expect(wrapper.emitted('update:preset')).toEqual([['last']])

    const picker = wrapper.getComponent({ name: 'EDatePicker' })
    await picker.vm.$emit('change', '2026-10-01')
    await picker.vm.$emit('change', ['2026-07-01', '2026-07-10'])

    expect(wrapper.emitted('update:range')).toEqual([[['2026-07-01', '2026-07-10']]])
  })
})
