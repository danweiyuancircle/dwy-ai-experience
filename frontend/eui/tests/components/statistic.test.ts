import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import EStatistic from '@/components/statistic/EStatistic.vue'

describe('EStatistic', () => {
  it('默认渲染，value 未传时显示 -', () => {
    const wrapper = mount(EStatistic)
    expect(wrapper.text()).toContain('-')
  })

  it('title prop 渲染标题', () => {
    const wrapper = mount(EStatistic, {
      props: { title: '总销售额' },
    })
    expect(wrapper.text()).toContain('总销售额')
  })

  it('value prop 为数字时渲染带千分位格式', () => {
    const wrapper = mount(EStatistic, {
      props: { title: '用户数', value: 12345 },
    })
    // toLocaleString 格式化数字
    expect(wrapper.text()).toContain('12')
    expect(wrapper.text()).toContain('345')
  })

  it('value prop 为字符串时直接渲染', () => {
    const wrapper = mount(EStatistic, {
      props: { value: 'N/A' },
    })
    expect(wrapper.text()).toContain('N/A')
  })

  it('prefix prop 渲染前缀', () => {
    const wrapper = mount(EStatistic, {
      props: { value: 100, prefix: '¥' },
    })
    expect(wrapper.text()).toContain('¥')
  })

  it('suffix prop 渲染后缀', () => {
    const wrapper = mount(EStatistic, {
      props: { value: 99.5, suffix: '%' },
    })
    expect(wrapper.text()).toContain('%')
  })

  it('precision prop 控制小数位数', () => {
    const wrapper = mount(EStatistic, {
      props: { value: 3.14159, precision: 2 },
    })
    expect(wrapper.text()).toContain('3.14')
  })

  it('precision 为 0 时取整数', () => {
    const wrapper = mount(EStatistic, {
      props: { value: 9.87, precision: 0 },
    })
    expect(wrapper.text()).toContain('10')
  })
})
