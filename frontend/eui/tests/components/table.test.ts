import { mount } from '@vue/test-utils'
import { describe, it, expect, beforeAll } from 'vitest'
import ETable from '@/components/table/ETable.vue'

beforeAll(() => {
  window.ResizeObserver = class {
    observe() {}
    unobserve() {}
    disconnect() {}
  } as any
})

const columns = [
  { key: 'name', title: '姓名' },
  { key: 'age', title: '年龄' },
]

const data = [
  { id: 1, name: '张三', age: 25 },
  { id: 2, name: '李四', age: 30 },
  { id: 3, name: '王五', age: 28 },
]

describe('ETable', () => {
  it('renders table element', () => {
    const wrapper = mount(ETable, {
      props: { columns, data },
    })
    expect(wrapper.find('table').exists()).toBe(true)
    expect(wrapper.find('[data-slot="table"]').exists()).toBe(true)
  })

  it('renders columns and data rows', () => {
    const wrapper = mount(ETable, {
      props: { columns, data },
    })
    const headers = wrapper.findAll('th')
    expect(headers.length).toBe(2)
    expect(headers[0].text()).toBe('姓名')
    expect(headers[1].text()).toBe('年龄')

    const rows = wrapper.findAll('tbody tr')
    expect(rows.length).toBe(3)
    expect(rows[0].text()).toContain('张三')
    expect(rows[0].text()).toContain('25')
  })

  it('shows empty text when data is empty', () => {
    const wrapper = mount(ETable, {
      props: { columns, data: [] },
    })
    expect(wrapper.text()).toContain('暂无数据')
  })

  it('shows custom empty text', () => {
    const wrapper = mount(ETable, {
      props: { columns, data: [], emptyText: '没有记录' },
    })
    expect(wrapper.text()).toContain('没有记录')
  })

  it('shows loading overlay when loading is true', () => {
    const wrapper = mount(ETable, {
      props: { columns, data, loading: true },
    })
    expect(wrapper.find('.animate-spin').exists()).toBe(true)
  })

  it('does not show loading overlay when loading is false', () => {
    const wrapper = mount(ETable, {
      props: { columns, data, loading: false },
    })
    expect(wrapper.find('.animate-spin').exists()).toBe(false)
  })

  it('renders selection checkboxes when selectable is true', () => {
    const wrapper = mount(ETable, {
      props: { columns, data, selectable: true, selectedKeys: [] },
    })
    const checkboxes = wrapper.findAll('input[type="checkbox"]')
    // 1 header checkbox + 3 row checkboxes
    expect(checkboxes.length).toBe(4)
  })

  it('applies striped class to alternate rows', () => {
    const wrapper = mount(ETable, {
      props: { columns, data, striped: true },
    })
    const rows = wrapper.findAll('tbody tr[data-slot="table-row"]')
    // Second row (index 1) should have striped class
    expect(rows[1].classes().join(' ')).toContain('bg-muted')
  })

  it('applies bordered class when bordered is true', () => {
    const wrapper = mount(ETable, {
      props: { columns, data, bordered: true },
    })
    expect(wrapper.find('[data-slot="table-container"]').classes().join(' ')).toContain('border')
  })

  it('emits row-click when a data row is clicked', async () => {
    const wrapper = mount(ETable, {
      props: { columns, data },
    })
    const rows = wrapper.findAll('tbody tr[data-slot="table-row"]')
    await rows[0].trigger('click')
    expect(wrapper.emitted('row-click')).toBeTruthy()
    expect(wrapper.emitted('row-click')![0]).toEqual([data[0], 0])
  })
})
