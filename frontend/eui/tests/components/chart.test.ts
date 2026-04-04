import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import EChartContainer from '@/components/chart/EChartContainer.vue'

const defaultConfig = {
  revenue: { label: 'Revenue', color: '#3b82f6' },
  profit: { label: 'Profit', color: '#10b981' },
}

describe('EChartContainer', () => {
  it('renders a chart container element', () => {
    const wrapper = mount(EChartContainer, {
      props: { config: defaultConfig },
    })
    expect(wrapper.find('[data-slot="chart"]').exists()).toBe(true)
  })

  it('sets CSS color variables from config', () => {
    const wrapper = mount(EChartContainer, {
      props: { config: defaultConfig },
    })
    const el = wrapper.find('[data-slot="chart"]').element as HTMLElement
    expect(el.style.getPropertyValue('--color-revenue')).toBe('#3b82f6')
    expect(el.style.getPropertyValue('--color-profit')).toBe('#10b981')
  })

  it('generates data-chart attribute', () => {
    const wrapper = mount(EChartContainer, {
      props: { config: defaultConfig },
    })
    expect(wrapper.find('[data-chart]').exists()).toBe(true)
  })

  it('uses custom id when provided', () => {
    const wrapper = mount(EChartContainer, {
      props: { config: defaultConfig, id: 'my-chart' },
    })
    expect(wrapper.find('[data-chart="my-chart"]').exists()).toBe(true)
  })

  it('renders slot content', () => {
    const wrapper = mount(EChartContainer, {
      props: { config: defaultConfig },
      slots: { default: '<svg class="test-chart"></svg>' },
    })
    expect(wrapper.find('.test-chart').exists()).toBe(true)
  })
})
