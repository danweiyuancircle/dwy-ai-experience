import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import EProgress from '@/components/progress/EProgress.vue'

describe('EProgress', () => {
  it('默认渲染', () => {
    const wrapper = mount(EProgress)
    expect(wrapper.find('[data-slot="progress"]').exists()).toBe(true)
    expect(wrapper.find('[data-slot="progress-indicator"]').exists()).toBe(true)
  })

  it('modelValue 默认为 0，进度条偏移 -100%', () => {
    const wrapper = mount(EProgress)
    const indicator = wrapper.find('[data-slot="progress-indicator"]')
    expect(indicator.attributes('style')).toContain('translateX(-100%)')
  })

  it('modelValue 为 50 时进度条偏移 -50%', () => {
    const wrapper = mount(EProgress, {
      props: { modelValue: 50 },
    })
    const indicator = wrapper.find('[data-slot="progress-indicator"]')
    expect(indicator.attributes('style')).toContain('translateX(-50%)')
  })

  it('modelValue 为 100 时进度条偏移 0%', () => {
    const wrapper = mount(EProgress, {
      props: { modelValue: 100 },
    })
    const indicator = wrapper.find('[data-slot="progress-indicator"]')
    expect(indicator.attributes('style')).toContain('translateX(-0%)')
  })

  it('支持自定义 class', () => {
    const wrapper = mount(EProgress, {
      props: { class: 'custom-progress' },
    })
    expect(wrapper.find('[data-slot="progress"]').classes()).toContain('custom-progress')
  })
})
