import { mount } from '@vue/test-utils'
import { describe, it, expect, beforeAll, beforeEach } from 'vitest'
import EPagination from '@/components/pagination/EPagination.vue'
import { mockViewportWidth } from '../helpers/mock-viewport'

beforeAll(() => {
  window.ResizeObserver = class {
    observe() {}
    unobserve() {}
    disconnect() {}
  } as any
})

describe('EPagination', () => {
  beforeEach(() => {
    mockViewportWidth(1024)
  })

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

  it('does not render first/last page arrow buttons', () => {
    const wrapper = mount(EPagination, {
      props: { total: 200, modelValue: 1, pageSize: 20 },
    })
    expect(wrapper.find('[data-slot="pagination-first"]').exists()).toBe(false)
    expect(wrapper.find('[data-slot="pagination-last"]').exists()).toBe(false)
  })

  it('still renders previous and next arrows', () => {
    const wrapper = mount(EPagination, {
      props: { total: 200, modelValue: 1, pageSize: 20 },
    })
    expect(wrapper.find('[data-slot="pagination-previous"]').exists()).toBe(true)
    expect(wrapper.find('[data-slot="pagination-next"]').exists()).toBe(true)
  })

  it('shows ellipsis and last page number when total pages exceed the window', () => {
    const wrapper = mount(EPagination, {
      props: { total: 220, modelValue: 1, pageSize: 20 },
    })
    const numbers = wrapper.findAll('[data-slot="pagination-item"]').map(item => item.text())
    expect(wrapper.find('[data-slot="pagination-ellipsis"]').exists()).toBe(true)
    expect(numbers).toContain('11')
  })

  it('simple mode shows current/total and hides size changer', () => {
    const wrapper = mount(EPagination, {
      props: {
        total: 100,
        modelValue: 2,
        pageSize: 10,
        mode: 'simple',
        showSizeChanger: true,
        showTotal: true,
        jumper: true,
      },
    })
    expect(wrapper.find('[data-slot="pagination-simple"]').text()).toContain('2 / 10')
    expect(wrapper.find('[data-slot="pagination-size-changer"]').exists()).toBe(false)
    expect(wrapper.find('[data-slot="pagination-jumper"]').exists()).toBe(false)
    expect(wrapper.find('[data-slot="pagination-item"]').exists()).toBe(false)
  })

  it('full mode keeps size changer even on a narrow viewport', () => {
    mockViewportWidth(375)
    const wrapper = mount(EPagination, {
      props: { total: 100, modelValue: 1, mode: 'full', showSizeChanger: true },
    })
    expect(wrapper.find('[data-slot="pagination-size-changer"]').exists()).toBe(true)
    expect(wrapper.find('[data-slot="pagination-simple"]').exists()).toBe(false)
  })

  it('auto mode uses simple layout on mobile', () => {
    mockViewportWidth(375)
    const wrapper = mount(EPagination, {
      props: { total: 100, modelValue: 1, pageSize: 10, showSizeChanger: true },
    })
    expect(wrapper.find('[data-slot="pagination-simple"]').exists()).toBe(true)
    expect(wrapper.find('[data-slot="pagination-size-changer"]').exists()).toBe(false)
  })
})

