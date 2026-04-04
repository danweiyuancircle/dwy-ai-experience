import { mount } from '@vue/test-utils'
import { describe, it, expect, beforeAll } from 'vitest'
import ESlider from '@/components/slider/ESlider.vue'

beforeAll(() => {
  // reka-ui SliderRoot 内部使用 ResizeObserver，jsdom 不提供该 API
  globalThis.ResizeObserver = class {
    observe() {}
    unobserve() {}
    disconnect() {}
  } as unknown as typeof ResizeObserver
})

describe('ESlider', () => {
  it('默认渲染 slider 元素', () => {
    const wrapper = mount(ESlider)
    expect(wrapper.find('[data-slot="slider"]').exists()).toBe(true)
  })

  it('渲染 track、range 和 thumb', () => {
    const wrapper = mount(ESlider, {
      props: { modelValue: [50] },
    })
    expect(wrapper.find('[data-slot="slider-track"]').exists()).toBe(true)
    expect(wrapper.find('[data-slot="slider-range"]').exists()).toBe(true)
    expect(wrapper.find('[data-slot="slider-thumb"]').exists()).toBe(true)
  })

  it('v-model 传递初始值', () => {
    const wrapper = mount(ESlider, {
      props: { modelValue: [30] },
    })
    expect(wrapper.find('[data-slot="slider"]').exists()).toBe(true)
  })

  it('多个 thumb 对应多值数组', () => {
    const wrapper = mount(ESlider, {
      props: { modelValue: [20, 80] },
    })
    const thumbs = wrapper.findAll('[data-slot="slider-thumb"]')
    expect(thumbs.length).toBe(2)
  })

  it('min/max props', () => {
    const wrapper = mount(ESlider, {
      props: { modelValue: [5], min: 0, max: 10 },
    })
    expect(wrapper.find('[data-slot="slider"]').exists()).toBe(true)
  })

  it('step prop', () => {
    const wrapper = mount(ESlider, {
      props: { modelValue: [50], step: 10 },
    })
    expect(wrapper.find('[data-slot="slider"]').exists()).toBe(true)
  })

  it('disabled prop 添加禁用状态', () => {
    const wrapper = mount(ESlider, {
      props: { modelValue: [50], disabled: true },
    })
    const root = wrapper.find('[data-slot="slider"]')
    expect(root.attributes('data-disabled')).toBeDefined()
  })

  it('orientation="vertical" 渲染垂直方向', () => {
    const wrapper = mount(ESlider, {
      props: { modelValue: [50], orientation: 'vertical' },
    })
    const root = wrapper.find('[data-slot="slider"]')
    expect(root.attributes('data-orientation')).toBe('vertical')
  })
})
