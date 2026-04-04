import { mount } from '@vue/test-utils'
import { describe, it, expect, beforeAll } from 'vitest'
import EPagination from '@/components/pagination/EPagination.vue'

beforeAll(() => {
  window.ResizeObserver = class {
    observe() {}
    unobserve() {}
    disconnect() {}
  } as any
})

describe('EPagination', () => {
  it('renders without errors', () => {
    const wrapper = mount(EPagination, {
      props: { total: 100, modelValue: 1 },
    })
    expect(wrapper.find('[data-slot="pagination-wrapper"]').exists()).toBe(true)
  })

  it('renders pagination root with correct total', () => {
    const wrapper = mount(EPagination, {
      props: { total: 50, modelValue: 1, pageSize: 10 },
    })
    expect(wrapper.find('[data-slot="pagination"]').exists()).toBe(true)
  })

  it('shows total text when showTotal is true', () => {
    const wrapper = mount(EPagination, {
      props: { total: 100, modelValue: 1, showTotal: true },
    })
    expect(wrapper.text()).toContain('共 100 条')
  })

  it('does not show total when showTotal is false', () => {
    const wrapper = mount(EPagination, {
      props: { total: 100, modelValue: 1, showTotal: false },
    })
    expect(wrapper.text()).not.toContain('共 100 条')
  })

  it('renders page size selector when showSizeChanger is true', () => {
    const wrapper = mount(EPagination, {
      props: { total: 100, modelValue: 1, showSizeChanger: true },
    })
    expect(wrapper.find('[data-slot="pagination-size-changer"]').exists()).toBe(true)
  })

  it('renders page size options', () => {
    const wrapper = mount(EPagination, {
      props: { total: 100, modelValue: 1, showSizeChanger: true, pageSizes: [10, 20, 50] },
    })
    const options = wrapper.findAll('option')
    expect(options.length).toBe(3)
    expect(options[0].text()).toBe('10 条/页')
    expect(options[1].text()).toBe('20 条/页')
    expect(options[2].text()).toBe('50 条/页')
  })

  it('applies disabled style when disabled is true', () => {
    const wrapper = mount(EPagination, {
      props: { total: 100, modelValue: 1, disabled: true },
    })
    const root = wrapper.find('[data-slot="pagination-wrapper"]')
    expect(root.classes().join(' ')).toContain('pointer-events-none')
  })

  it('renders jumper when jumper is true', () => {
    const wrapper = mount(EPagination, {
      props: { total: 100, modelValue: 1, jumper: true, layout: 'pager, jumper' },
    })
    expect(wrapper.find('[data-slot="pagination-jumper"]').exists()).toBe(true)
    expect(wrapper.text()).toContain('前往')
    expect(wrapper.text()).toContain('页')
  })

  it('does not render jumper when jumper is false', () => {
    const wrapper = mount(EPagination, {
      props: { total: 100, modelValue: 1, jumper: false },
    })
    expect(wrapper.find('[data-slot="pagination-jumper"]').exists()).toBe(false)
  })
})
