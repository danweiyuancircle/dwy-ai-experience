import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import ETimeline from '@/components/timeline/ETimeline.vue'

const items = [
  { title: '创建订单', content: '订单已创建', timestamp: '2024-01-01' },
  { title: '付款成功', content: '支付完成', timestamp: '2024-01-02', type: 'success' as const },
  { title: '发货', timestamp: '2024-01-03', type: 'warning' as const },
]

describe('ETimeline', () => {
  it('renders without errors', () => {
    const wrapper = mount(ETimeline, {
      props: { items },
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('renders all timeline items', () => {
    const wrapper = mount(ETimeline, {
      props: { items },
    })
    expect(wrapper.text()).toContain('创建订单')
    expect(wrapper.text()).toContain('付款成功')
    expect(wrapper.text()).toContain('发货')
  })

  it('renders content and timestamps', () => {
    const wrapper = mount(ETimeline, {
      props: { items },
    })
    expect(wrapper.text()).toContain('订单已创建')
    expect(wrapper.text()).toContain('2024-01-01')
    expect(wrapper.text()).toContain('支付完成')
    expect(wrapper.text()).toContain('2024-01-02')
  })

  it('renders items in original order by default', () => {
    const wrapper = mount(ETimeline, {
      props: { items },
    })
    const titles = wrapper.findAll('.font-medium.leading-none')
    expect(titles[0].text()).toBe('创建订单')
    expect(titles[1].text()).toBe('付款成功')
    expect(titles[2].text()).toBe('发货')
  })

  it('renders items in reverse order when reverse is true', () => {
    const wrapper = mount(ETimeline, {
      props: { items, reverse: true },
    })
    const titles = wrapper.findAll('.font-medium.leading-none')
    expect(titles[0].text()).toBe('发货')
    expect(titles[1].text()).toBe('付款成功')
    expect(titles[2].text()).toBe('创建订单')
  })

  it('applies success dot color for success type', () => {
    const wrapper = mount(ETimeline, {
      props: { items: [{ title: 'OK', type: 'success' as const }] },
    })
    const dot = wrapper.find('.rounded-full')
    expect(dot.classes()).toContain('bg-green-500')
  })

  it('applies warning dot color for warning type', () => {
    const wrapper = mount(ETimeline, {
      props: { items: [{ title: 'Warn', type: 'warning' as const }] },
    })
    const dot = wrapper.find('.rounded-full')
    expect(dot.classes()).toContain('bg-yellow-500')
  })

  it('applies danger dot color for danger type', () => {
    const wrapper = mount(ETimeline, {
      props: { items: [{ title: 'Err', type: 'danger' as const }] },
    })
    const dot = wrapper.find('.rounded-full')
    expect(dot.classes()).toContain('bg-red-500')
  })

  it('applies default (primary) dot color when no type', () => {
    const wrapper = mount(ETimeline, {
      props: { items: [{ title: 'Default' }] },
    })
    const dot = wrapper.find('.rounded-full')
    expect(dot.classes()).toContain('bg-primary')
  })
})
