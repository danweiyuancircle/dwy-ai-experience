import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import EDescriptions from '@/components/descriptions/EDescriptions.vue'

const items = [
  { label: '姓名', value: '张三' },
  { label: '年龄', value: 25 },
  { label: '城市', value: '北京' },
]

describe('EDescriptions', () => {
  it('renders without errors', () => {
    const wrapper = mount(EDescriptions, {
      props: { items },
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('renders items with labels and values', () => {
    const wrapper = mount(EDescriptions, {
      props: { items },
    })
    expect(wrapper.text()).toContain('姓名')
    expect(wrapper.text()).toContain('张三')
    expect(wrapper.text()).toContain('年龄')
    expect(wrapper.text()).toContain('25')
    expect(wrapper.text()).toContain('城市')
    expect(wrapper.text()).toContain('北京')
  })

  it('uses default columns of 2', () => {
    const wrapper = mount(EDescriptions, {
      props: { items },
    })
    const grid = wrapper.find('.grid')
    // 2 columns * 2 (label + value) = 4 template columns
    expect(grid.attributes('style')).toContain('grid-template-columns: repeat(4, minmax(0, 1fr))')
  })

  it('applies custom columns count', () => {
    const wrapper = mount(EDescriptions, {
      props: { items, columns: 3 },
    })
    const grid = wrapper.find('.grid')
    // 3 columns * 2 = 6 template columns
    expect(grid.attributes('style')).toContain('grid-template-columns: repeat(6, minmax(0, 1fr))')
  })

  it('applies bordered style', () => {
    const wrapper = mount(EDescriptions, {
      props: { items, bordered: true },
    })
    const grid = wrapper.find('.grid')
    expect(grid.classes().join(' ')).toContain('border')
  })

  it('does not apply bordered style by default', () => {
    const wrapper = mount(EDescriptions, {
      props: { items },
    })
    const grid = wrapper.find('.grid')
    expect(grid.classes().join(' ')).not.toContain('border')
  })

  it('renders title when provided', () => {
    const wrapper = mount(EDescriptions, {
      props: { items, title: '用户信息' },
    })
    expect(wrapper.text()).toContain('用户信息')
  })

  it('does not render title section when title is not provided', () => {
    const wrapper = mount(EDescriptions, {
      props: { items },
    })
    expect(wrapper.find('.font-semibold').exists()).toBe(false)
  })

  it('renders empty when items is empty', () => {
    const wrapper = mount(EDescriptions, {
      props: { items: [] },
    })
    const grid = wrapper.find('.grid')
    expect(grid.exists()).toBe(true)
    // No label/value children
    expect(grid.element.children.length).toBe(0)
  })
})
