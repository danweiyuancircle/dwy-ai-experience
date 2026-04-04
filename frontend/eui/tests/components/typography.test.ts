import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import ETypography from '@/components/typography/ETypography.vue'

describe('ETypography', () => {
  it('默认渲染为 p 标签', () => {
    const wrapper = mount(ETypography, {
      slots: { default: '段落文本' },
    })
    expect(wrapper.element.tagName).toBe('P')
    expect(wrapper.text()).toBe('段落文本')
  })

  it('variant 为 h1 时渲染 h1 标签', () => {
    const wrapper = mount(ETypography, {
      props: { variant: 'h1' },
      slots: { default: '一级标题' },
    })
    expect(wrapper.element.tagName).toBe('H1')
    expect(wrapper.text()).toBe('一级标题')
  })

  it('variant 为 h2 时渲染 h2 标签', () => {
    const wrapper = mount(ETypography, {
      props: { variant: 'h2' },
      slots: { default: '二级标题' },
    })
    expect(wrapper.element.tagName).toBe('H2')
  })

  it('variant 为 small 时渲染 small 标签', () => {
    const wrapper = mount(ETypography, {
      props: { variant: 'small' },
      slots: { default: '小文本' },
    })
    expect(wrapper.element.tagName).toBe('SMALL')
  })

  it('variant 为 large 时渲染 div 标签', () => {
    const wrapper = mount(ETypography, {
      props: { variant: 'large' },
      slots: { default: '大文本' },
    })
    expect(wrapper.element.tagName).toBe('DIV')
  })

  it('as prop 覆盖默认标签', () => {
    const wrapper = mount(ETypography, {
      props: { variant: 'h1', as: 'span' },
      slots: { default: '自定义标签' },
    })
    expect(wrapper.element.tagName).toBe('SPAN')
  })

  it('slot 内容正确渲染', () => {
    const wrapper = mount(ETypography, {
      slots: { default: '<strong>加粗内容</strong>' },
    })
    expect(wrapper.find('strong').exists()).toBe(true)
    expect(wrapper.find('strong').text()).toBe('加粗内容')
  })

  it('data-slot 属性存在', () => {
    const wrapper = mount(ETypography)
    expect(wrapper.attributes('data-slot')).toBe('typography')
  })

  it('variant 为 muted 时渲染 p 标签并应用 muted 样式类', () => {
    const wrapper = mount(ETypography, {
      props: { variant: 'muted' },
      slots: { default: '灰色文本' },
    })
    expect(wrapper.element.tagName).toBe('P')
    expect(wrapper.classes()).toContain('text-muted-foreground')
  })
})
