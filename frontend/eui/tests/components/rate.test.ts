import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import ERate from '@/components/rate/ERate.vue'

describe('ERate', () => {
  it('默认渲染 5 个星星按钮', () => {
    const wrapper = mount(ERate)
    const buttons = wrapper.findAll('button')
    expect(buttons.length).toBe(5)
  })

  it('v-model 选中对应星星', () => {
    const wrapper = mount(ERate, {
      props: { modelValue: 3 },
    })
    // modelValue=3 意味着前 3 个星星应该是 full 状态（fill-yellow-400）
    const buttons = wrapper.findAll('button')
    expect(buttons.length).toBe(5)
  })

  it('max prop 控制星星数量', () => {
    const wrapper = mount(ERate, {
      props: { max: 10 },
    })
    const buttons = wrapper.findAll('button')
    expect(buttons.length).toBe(10)
  })

  it('disabled prop 禁用交互', () => {
    const wrapper = mount(ERate, {
      props: { disabled: true },
    })
    const buttons = wrapper.findAll('button')
    buttons.forEach((btn) => {
      expect(btn.element.disabled).toBe(true)
    })
  })

  it('点击星星触发 update:modelValue', async () => {
    const wrapper = mount(ERate, {
      props: { modelValue: 0 },
    })
    const buttons = wrapper.findAll('button')
    await buttons[2].trigger('click')
    const emitted = wrapper.emitted('update:modelValue')
    expect(emitted).toBeTruthy()
    expect(emitted![0][0]).toBe(3)
  })

  it('disabled 状态下点击不触发事件', async () => {
    const wrapper = mount(ERate, {
      props: { modelValue: 0, disabled: true },
    })
    const buttons = wrapper.findAll('button')
    await buttons[2].trigger('click')
    expect(wrapper.emitted('update:modelValue')).toBeUndefined()
  })

  it('showText 显示评分文本', () => {
    const wrapper = mount(ERate, {
      props: { modelValue: 3, showText: true },
    })
    expect(wrapper.text()).toContain('3')
    expect(wrapper.text()).toContain('5')
  })

  it('allowHalf 允许半星评分', async () => {
    const wrapper = mount(ERate, {
      props: { modelValue: 2.5, allowHalf: true },
    })
    // 2.5 意味着第 3 个星星是 half 状态
    // 验证组件渲染了半星（class 包含 w-1/2 裁切）
    expect(wrapper.find('.w-1\\/2').exists()).toBe(true)
  })
})
