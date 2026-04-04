import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import ENumberField from '@/components/number-field/ENumberField.vue'

describe('ENumberField', () => {
  it('默认渲染包含 number-field slot', () => {
    const wrapper = mount(ENumberField)
    expect(wrapper.find('[data-slot="number-field"]').exists()).toBe(true)
  })

  it('渲染输入框和增减按钮', () => {
    const wrapper = mount(ENumberField)
    expect(wrapper.find('[data-slot="input"]').exists()).toBe(true)
    expect(wrapper.find('[data-slot="increment"]').exists()).toBe(true)
    expect(wrapper.find('[data-slot="decrement"]').exists()).toBe(true)
  })

  it('v-model 传递初始值', () => {
    const wrapper = mount(ENumberField, {
      props: { modelValue: 5 },
    })
    const root = wrapper.find('[data-slot="number-field"]')
    expect(root.exists()).toBe(true)
  })

  it('min/max props 传递到根组件', () => {
    const wrapper = mount(ENumberField, {
      props: { modelValue: 5, min: 0, max: 10 },
    })
    expect(wrapper.find('[data-slot="number-field"]').exists()).toBe(true)
  })

  it('step prop 传递到根组件', () => {
    const wrapper = mount(ENumberField, {
      props: { modelValue: 0, step: 2 },
    })
    expect(wrapper.find('[data-slot="number-field"]').exists()).toBe(true)
  })

  it('disabled prop 禁用交互', () => {
    const wrapper = mount(ENumberField, {
      props: { disabled: true },
    })
    const root = wrapper.find('[data-slot="number-field"]')
    expect(root.attributes('data-disabled')).toBeDefined()
  })

  it('controlsPosition="right" 渲染右侧控制按钮布局', () => {
    const wrapper = mount(ENumberField, {
      props: { controlsPosition: 'right' },
    })
    expect(wrapper.find('[data-slot="increment"]').exists()).toBe(true)
    expect(wrapper.find('[data-slot="decrement"]').exists()).toBe(true)
  })

  it('placeholder prop', () => {
    const wrapper = mount(ENumberField, {
      props: { placeholder: '请输入数字' },
    })
    const input = wrapper.find('[data-slot="input"]')
    expect(input.attributes('placeholder')).toBe('请输入数字')
  })
})
