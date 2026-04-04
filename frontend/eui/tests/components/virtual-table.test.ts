import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import EVirtualTable from '@/components/virtual-table/EVirtualTable.vue'

const columns = [
  { key: 'name', title: '姓名' },
  { key: 'score', title: '分数', align: 'center' as const },
]

const data = [
  { id: 1, name: '张三', score: 90 },
  { id: 2, name: '李四', score: 85 },
]

describe('EVirtualTable', () => {
  it('renders table element', () => {
    const wrapper = mount(EVirtualTable, {
      props: { columns, data },
    })
    expect(wrapper.find('table').exists()).toBe(true)
  })

  it('renders column headers', () => {
    const wrapper = mount(EVirtualTable, {
      props: { columns, data },
    })
    const headers = wrapper.findAll('th')
    expect(headers.length).toBe(2)
    expect(headers[0].text()).toBe('姓名')
    expect(headers[1].text()).toBe('分数')
  })

  it('renders data rows', () => {
    const wrapper = mount(EVirtualTable, {
      props: { columns, data },
    })
    const rows = wrapper.findAll('tbody tr')
    expect(rows.length).toBe(2)
    expect(rows[0].text()).toContain('张三')
    expect(rows[0].text()).toContain('90')
  })

  it('applies specified height to container', () => {
    const wrapper = mount(EVirtualTable, {
      props: { columns, data, height: 500 },
    })
    const container = wrapper.element as HTMLElement
    expect(container.style.height).toBe('500px')
  })

  it('uses default height of 400px', () => {
    const wrapper = mount(EVirtualTable, {
      props: { columns, data },
    })
    const container = wrapper.element as HTMLElement
    expect(container.style.height).toBe('400px')
  })

  it('shows loading overlay when loading is true', () => {
    const wrapper = mount(EVirtualTable, {
      props: { columns, data, loading: true },
    })
    expect(wrapper.find('.animate-spin').exists()).toBe(true)
  })

  it('does not show loading overlay when loading is false', () => {
    const wrapper = mount(EVirtualTable, {
      props: { columns, data, loading: false },
    })
    expect(wrapper.find('.animate-spin').exists()).toBe(false)
  })

  it('shows empty text when data is empty', () => {
    const wrapper = mount(EVirtualTable, {
      props: { columns, data: [] },
    })
    expect(wrapper.text()).toContain('No data')
  })

  it('shows custom empty text', () => {
    const wrapper = mount(EVirtualTable, {
      props: { columns, data: [], emptyText: '暂无数据' },
    })
    expect(wrapper.text()).toContain('暂无数据')
  })

  it('emits row-click when a row is clicked', async () => {
    const wrapper = mount(EVirtualTable, {
      props: { columns, data },
    })
    const rows = wrapper.findAll('tbody tr')
    await rows[0].trigger('click')
    expect(wrapper.emitted('row-click')).toBeTruthy()
    expect(wrapper.emitted('row-click')![0]).toEqual([data[0], 0])
  })
})
