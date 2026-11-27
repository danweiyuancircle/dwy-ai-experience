/**
 * RecordBoard：说明、筛选、汇总、明细四区。缺的区不渲染。
 */
import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import { RecordBoard, RecordMetric } from '../../../src/components'

describe('RecordBoard', () => {
  it('四区按说明、筛选、汇总、明细排列', () => {
    const wrapper = mount(RecordBoard, {
      props: { summaryTitle: '按当前筛选汇总' },
      slots: {
        notice: '<p class="notice-mark">说明</p>',
        filters: '<button class="filter-mark">本月</button>',
        summary: '<span class="metric-mark">12</span>',
        default: '<div class="table-mark">表</div>',
      },
    })

    const text = wrapper.text()
    expect(text.indexOf('说明')).toBeLessThan(text.indexOf('本月'))
    expect(text.indexOf('本月')).toBeLessThan(text.indexOf('按当前筛选汇总'))
    expect(text.indexOf('按当前筛选汇总')).toBeLessThan(text.indexOf('表'))
    expect(wrapper.find('.record-board-filters').find('button.filter-mark').exists()).toBe(true)
    expect(wrapper.find('.record-board-summary').text()).toContain('12')
    expect(wrapper.find('.record-board-metrics').classes()).toContain('justify-center')
    expect(wrapper.find('.record-board-body').classes()).toContain('flex-1')
    expect(wrapper.find('.table-mark').exists()).toBe(true)
  })

  it('没传说明和汇总时不渲染这两区', () => {
    const wrapper = mount(RecordBoard, {
      slots: { default: '<div class="table-mark">表</div>' },
    })

    expect(wrapper.find('.record-board-notice').exists()).toBe(false)
    expect(wrapper.find('.record-board-filters').exists()).toBe(false)
    expect(wrapper.find('.record-board-summary').exists()).toBe(false)
    expect(wrapper.find('.table-mark').exists()).toBe(true)
  })
})

describe('RecordMetric', () => {
  it('展示标签和值，danger 才强调数值', () => {
    const plain = mount(RecordMetric, { props: { label: '请求次数', value: 7 } })
    const danger = mount(RecordMetric, { props: { label: '失败留痕', value: 2, tone: 'danger' } })

    expect(plain.text()).toContain('请求次数')
    expect(plain.text()).toContain('7')
    expect(plain.classes()).not.toContain('text-destructive')
    expect(danger.text()).toContain('2')
    expect(danger.classes()).toContain('text-destructive')
  })
})
