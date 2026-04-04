import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import EEmpty from '@/components/empty/EEmpty.vue'

describe('EEmpty', () => {
  it('renders an empty element with data-slot attribute', () => {
    const wrapper = mount(EEmpty)
    expect(wrapper.find('[data-slot="empty"]').exists()).toBe(true)
  })

  it('applies default empty classes', () => {
    const wrapper = mount(EEmpty)
    const el = wrapper.find('[data-slot="empty"]')
    expect(el.classes()).toContain('flex')
    expect(el.classes()).toContain('items-center')
    expect(el.classes()).toContain('border-dashed')
  })

  it('renders title when title prop is provided', () => {
    const wrapper = mount(EEmpty, { props: { title: '暂无数据' } })
    const title = wrapper.find('[data-slot="empty-title"]')
    expect(title.exists()).toBe(true)
    expect(title.text()).toBe('暂无数据')
  })

  it('renders description when description prop is provided', () => {
    const wrapper = mount(EEmpty, { props: { description: '请稍后再试' } })
    const desc = wrapper.find('[data-slot="empty-description"]')
    expect(desc.exists()).toBe(true)
    expect(desc.text()).toBe('请稍后再试')
  })

  it('does not render title element when title is not provided', () => {
    const wrapper = mount(EEmpty)
    expect(wrapper.find('[data-slot="empty-title"]').exists()).toBe(false)
  })

  it('does not render description element when description is not provided', () => {
    const wrapper = mount(EEmpty)
    expect(wrapper.find('[data-slot="empty-description"]').exists()).toBe(false)
  })

  it('renders icon slot content', () => {
    const wrapper = mount(EEmpty, {
      slots: { icon: '<svg class="test-icon"></svg>' },
    })
    const iconWrapper = wrapper.find('[data-slot="empty-icon"]')
    expect(iconWrapper.exists()).toBe(true)
    expect(iconWrapper.find('.test-icon').exists()).toBe(true)
  })

  it('renders icon area when icon prop is provided', () => {
    const wrapper = mount(EEmpty, { props: { icon: '📭' } })
    const iconWrapper = wrapper.find('[data-slot="empty-icon"]')
    expect(iconWrapper.exists()).toBe(true)
    expect(iconWrapper.text()).toBe('📭')
  })

  it('does not render icon area when neither icon prop nor icon slot is provided', () => {
    const wrapper = mount(EEmpty)
    expect(wrapper.find('[data-slot="empty-icon"]').exists()).toBe(false)
  })

  it('renders default slot content', () => {
    const wrapper = mount(EEmpty, {
      slots: { default: '<button>重新加载</button>' },
    })
    expect(wrapper.text()).toContain('重新加载')
  })

  it('merges custom class with default classes', () => {
    const wrapper = mount(EEmpty, { props: { class: 'my-custom-class' } })
    const el = wrapper.find('[data-slot="empty"]')
    expect(el.classes()).toContain('my-custom-class')
    expect(el.classes()).toContain('flex')
  })
})
