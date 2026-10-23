/**
 * ConfigFieldControl：按种类画控件。字节换单位不改已存值。
 */
import { defineComponent } from 'vue'
import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import { ConfigFieldControl } from '../../../src/components'

const ENumberField = defineComponent({
  name: 'ENumberField',
  props: {
    modelValue: { type: Number, default: undefined },
    min: { type: Number, default: undefined },
    max: { type: Number, default: undefined },
    step: { type: Number, default: undefined },
    precision: { type: Number, default: undefined },
  },
  emits: ['update:modelValue'],
  template: '<input class="num" />',
})

const ESelect = defineComponent({
  name: 'ESelect',
  props: {
    modelValue: { type: String, default: '' },
    options: { type: Array, default: () => [] },
  },
  emits: ['update:modelValue'],
  template: '<button class="unit" type="button" @click="$emit(\'update:modelValue\', \'GB\')">{{ modelValue }}</button>',
})

const EInput = defineComponent({
  name: 'EInput',
  props: {
    modelValue: { type: String, default: '' },
    maxlength: { type: Number, default: undefined },
  },
  template: '<input class="text" />',
})

const ESwitch = defineComponent({
  name: 'ESwitch',
  props: { modelValue: { type: Boolean, default: false } },
  template: '<button class="switch" type="button" />',
})

const MB = 1024 ** 2

describe('ConfigFieldControl', () => {
  // 使用正式 EUI 控件验证日期空态，避免业务侧硬编码文案掩盖基础库问题。
  it('可选日期留空使用 EUI 中文文案，外部清空不写入今天', async () => {
    const wrapper = mount(ConfigFieldControl, {
      props: { modelValue: '', spec: { kind: 'date', required: false } },
    })

    expect(wrapper.text()).toContain('请选择日期')
    expect(wrapper.text()).not.toContain('Pick a date')

    await wrapper.setProps({ modelValue: '2026-10-01' })
    expect(wrapper.text()).toContain('2026-10-01')
    await wrapper.setProps({ modelValue: '' })
    expect(wrapper.text()).toContain('请选择日期')
    expect(wrapper.emitted('update:modelValue')).toBeUndefined()
    wrapper.unmount()
  })

  it('小数步进 0.01，避免 0.8 被吸走', () => {
    const wrapper = mount(ConfigFieldControl, {
      props: {
        modelValue: 0.8,
        spec: { kind: 'float', min: 0.01, max: 100 },
      },
      global: { stubs: { ENumberField, ESelect, EInput, ESwitch } },
    })

    const field = wrapper.getComponent({ name: 'ENumberField' })
    expect(field.props('step')).toBe(0.01)
    expect(field.props('min')).toBe(0.01)
    expect(field.props('precision')).toBe(2)
  })

  it('体积按传入的换算显示，换单位不改字节', async () => {
    const wrapper = mount(ConfigFieldControl, {
      props: {
        modelValue: 500 * MB,
        unit: 'MB',
        spec: {
          kind: 'byte',
          precision: 2,
          unitOptions: [{ label: 'MB', value: 'MB' }, { label: 'GB', value: 'GB' }],
          fromBytes: (bytes: number) => bytes / MB,
          toBytes: (amount: number) => Math.round(amount * MB),
        },
      },
      global: { stubs: { ENumberField, ESelect, EInput, ESwitch } },
    })

    expect(wrapper.getComponent({ name: 'ENumberField' }).props('modelValue')).toBe(500)

    await wrapper.get('.unit').trigger('click')
    expect(wrapper.emitted('update:unit')).toEqual([['GB']])
    expect(wrapper.emitted('update:modelValue')).toBeUndefined()
  })

  it('改体积数字时写回字节', async () => {
    const wrapper = mount(ConfigFieldControl, {
      props: {
        modelValue: 0,
        unit: 'MB',
        spec: {
          kind: 'byte',
          fromBytes: (bytes: number) => bytes / MB,
          toBytes: (amount: number) => Math.round(amount * MB),
        },
      },
      global: { stubs: { ENumberField, ESelect, EInput, ESwitch } },
    })

    await wrapper.getComponent({ name: 'ENumberField' }).vm.$emit('update:modelValue', 2)
    expect(wrapper.emitted('update:modelValue')).toEqual([[2 * MB]])
  })

  it('字符串带长度上限，布尔走开关', () => {
    const text = mount(ConfigFieldControl, {
      props: { modelValue: '0.2.0', spec: { kind: 'string', maxLength: 32 } },
      global: { stubs: { ENumberField, ESelect, EInput, ESwitch } },
    })
    const flag = mount(ConfigFieldControl, {
      props: { modelValue: true, spec: { kind: 'bool' } },
      global: { stubs: { ENumberField, ESelect, EInput, ESwitch } },
    })

    expect(text.getComponent({ name: 'EInput' }).props('maxlength')).toBe(32)
    expect(flag.findComponent({ name: 'ESwitch' }).exists()).toBe(true)
    expect(flag.findComponent({ name: 'EInput' }).exists()).toBe(false)
  })

  it('900 秒显示成 15 分钟，换单位不改秒数', async () => {
    const HourSelect = defineComponent({
      name: 'ESelect',
      props: { modelValue: { type: String, default: '' }, options: { type: Array, default: () => [] } },
      emits: ['update:modelValue'],
      template: '<button class="unit" type="button" @click="$emit(\'update:modelValue\', \'小时\')">{{ modelValue }}</button>',
    })
    const wrapper = mount(ConfigFieldControl, {
      props: { modelValue: 900, spec: { kind: 'duration', min: 60, max: 86400 } },
      global: { stubs: { ENumberField, ESelect: HourSelect, EInput, ESwitch } },
    })

    expect(wrapper.getComponent({ name: 'ENumberField' }).props('modelValue')).toBe(15)
    expect(wrapper.get('.unit').text()).toBe('分钟')

    await wrapper.get('.unit').trigger('click')
    expect(wrapper.emitted('update:modelValue')).toBeUndefined()
    expect(wrapper.getComponent({ name: 'ENumberField' }).props('modelValue')).toBe(0.25)
  })
})
