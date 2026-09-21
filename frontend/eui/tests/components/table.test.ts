import { mount } from '@vue/test-utils'
import { describe, it, expect, beforeAll, afterEach } from 'vitest'
import { h } from 'vue'
import ETable from '@/components/table/ETable.vue'
import { mockViewportWidth } from '../helpers/mock-viewport'

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

  it('表宽默认铺满容器，长文案不把表撑出视口', () => {
    const wrapper = mount(ETable, {
      props: { columns, data },
    })
    const table = wrapper.find('[data-slot="table"]')
    expect(table.classes()).toContain('w-full')
    expect(table.classes()).not.toContain('w-max')
    expect(wrapper.find('[data-slot="table-container"]').classes()).toContain('overflow-auto')
    expect(wrapper.find('[data-slot="table-container"]').classes()).toContain('overscroll-x-contain')
  })

  it('列声明数字 width 时表 minWidth 为列宽之和，窄容器才能横滑而不是压列', () => {
    const wrapper = mount(ETable, {
      props: {
        columns: [
          { key: 'name', title: '姓名', width: 160 },
          { key: 'age', title: '年龄', width: 120 },
        ],
        data,
      },
    })
    const table = wrapper.find('[data-slot="table"]')
    expect(table.attributes('style')).toMatch(/min-width:\s*280px/)
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

  it('virtual=true 仍渲染表头和容器（滚动窗口交给 vue-virtual）', () => {
    const wrapper = mount(ETable, {
      props: { columns, data, virtual: true, virtualRowHeight: 48 },
    })
    expect(wrapper.find('[data-slot="table"]').exists()).toBe(true)
    expect(wrapper.find('[data-slot="table-container"]').exists()).toBe(true)
    expect(wrapper.findAll('th').length).toBe(2)
  })
})

describe('mobileLayout stack', () => {
  const nativeMatchMedia = window.matchMedia

  afterEach(() => {
    window.matchMedia = nativeMatchMedia
  })

  const stackColumns = [
    { key: 'name', title: '姓名' },
    { key: 'logic', title: '因子逻辑' },
  ]
  const stackData = [
    { id: 1, name: '张三', logic: '价量背离短逻辑' },
  ]

  it('默认 scroll 窄屏仍是表', () => {
    mockViewportWidth(375)
    const wrapper = mount(ETable, { props: { columns: stackColumns, data: stackData } })
    expect(wrapper.find('[data-slot="table"]').exists()).toBe(true)
    expect(wrapper.find('[data-slot="table-stack"]').exists()).toBe(false)
  })

  it('stack + 桌面仍是表', () => {
    mockViewportWidth(1024)
    const wrapper = mount(ETable, {
      props: { columns: stackColumns, data: stackData, mobileLayout: 'stack' },
    })
    expect(wrapper.find('[data-slot="table"]').exists()).toBe(true)
    expect(wrapper.find('[data-slot="table-stack"]').exists()).toBe(false)
  })

  it('stack + 窄屏出卡片', () => {
    mockViewportWidth(375)
    const wrapper = mount(ETable, {
      props: { columns: stackColumns, data: stackData, mobileLayout: 'stack' },
    })
    expect(wrapper.find('table').exists()).toBe(false)
    expect(wrapper.find('[data-slot="table-stack"]').exists()).toBe(true)
    expect(wrapper.findAll('[data-slot="table-stack-item"]').length).toBe(1)
  })

  it('卡片含列 title 与单元格值', () => {
    mockViewportWidth(375)
    const wrapper = mount(ETable, {
      props: { columns: stackColumns, data: stackData, mobileLayout: 'stack' },
    })
    const item = wrapper.find('[data-slot="table-stack-item"]')
    expect(item.text()).toContain('因子逻辑')
    expect(item.text()).toContain('价量背离短逻辑')
    expect(item.text()).toContain('姓名')
    expect(item.text()).toContain('张三')
  })

  it('#cell-* 在卡片生效', () => {
    mockViewportWidth(375)
    const wrapper = mount(ETable, {
      props: { columns: stackColumns, data: stackData, mobileLayout: 'stack' },
      slots: {
        'cell-logic': () => h('span', { class: 'slot-logic' }, '插槽逻辑'),
      },
    })
    expect(wrapper.find('.slot-logic').text()).toBe('插槽逻辑')
    expect(wrapper.text()).not.toContain('价量背离短逻辑')
  })

  it('整卡点击 emit row-click', async () => {
    mockViewportWidth(375)
    const wrapper = mount(ETable, {
      props: { columns: stackColumns, data: stackData, mobileLayout: 'stack' },
    })
    await wrapper.find('[data-slot="table-stack-item"]').trigger('click')
    expect(wrapper.emitted('row-click')![0]).toEqual([stackData[0], 0])
  })

  it('#actions 在卡片底且不冒泡', async () => {
    mockViewportWidth(375)
    const wrapper = mount(ETable, {
      props: { columns: stackColumns, data: stackData, mobileLayout: 'stack' },
      slots: {
        actions: () => h('button', { class: 'row-action' }, '操作'),
      },
    })
    expect(wrapper.find('.row-action').exists()).toBe(true)
    await wrapper.find('.row-action').trigger('click')
    expect(wrapper.emitted('row-click')).toBeFalsy()
  })

  it('长文本换行，无 whitespace-nowrap', () => {
    mockViewportWidth(375)
    const wrapper = mount(ETable, {
      props: { columns: stackColumns, data: stackData, mobileLayout: 'stack' },
    })
    const html = wrapper.find('[data-slot="table-stack"]').html()
    expect(html).toContain('break-words')
    expect(html).not.toContain('whitespace-nowrap')
  })

  it('stack + virtual 窄屏不崩，无 virtual spacer', () => {
    mockViewportWidth(375)
    const wrapper = mount(ETable, {
      props: {
        columns: stackColumns,
        data: stackData,
        mobileLayout: 'stack',
        virtual: true,
        virtualRowHeight: 48,
      },
    })
    expect(wrapper.find('[data-slot="table-stack-item"]').exists()).toBe(true)
    expect(wrapper.find('table').exists()).toBe(false)
    expect(wrapper.find('[aria-hidden="true"]').exists()).toBe(false)
  })
})
