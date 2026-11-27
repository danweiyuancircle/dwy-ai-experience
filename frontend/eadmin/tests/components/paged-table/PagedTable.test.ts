/**
 * PagedTable：顶栏不进表格、分页按 total 显隐、排序和行点击原样抛出。
 */
import { defineComponent, h } from 'vue'
import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import { PagedTable } from '../../../src/components'

const TableStub = defineComponent({
  name: 'ETable',
  props: {
    data: { type: Array, default: () => [] },
    columns: { type: Array, default: () => [] },
    rowKey: { type: String, default: 'id' },
  },
  emits: ['sort', 'row-click', 'update:expandedRowKeys'],
  setup(props, { slots }) {
    return () =>
      h('div', { class: 'table-stub' }, [
        slots.toolbar ? h('span', { class: 'toolbar-leak' }, 'leak') : null,
        slots.actions ? h('span', { class: 'actions-leak' }, 'leak') : null,
        slots['cell-name']?.({ row: { name: '甲' }, value: '甲' }),
        (props.data as unknown[]).length === 0 ? slots.empty?.({}) : null,
      ])
  },
})

const PaginationStub = defineComponent({
  name: 'EPagination',
  props: {
    modelValue: { type: Number, default: 1 },
    total: { type: Number, default: 0 },
    pageSize: { type: Number, default: 10 },
    pageSizes: { type: Array, default: () => [] },
    showTotal: { type: Boolean, default: false },
    showSizeChanger: { type: Boolean, default: false },
  },
  emits: ['update:modelValue', 'update:pageSize'],
  template: '<div class="pager-stub" />',
})

/** 挂上表格和分页 stub，避免 happy-dom 渲染不出 eui 表格单元格 */
function mountList(props: Record<string, unknown> = {}, withToolbar = true) {
  return mount(PagedTable, {
    props: {
      columns: [{ key: 'name', title: '名称', sortable: true }],
      data: [{ name: '甲' }],
      page: 2,
      pageSize: 50,
      total: 80,
      ...props,
    },
    slots: {
      ...(withToolbar ? { toolbar: '<button class="query">查询</button>' } : {}),
      'cell-name': '<span class="cell-name">甲</span>',
      empty: '<span class="empty-mark">空</span>',
    },
    global: {
      stubs: {
        ETable: TableStub,
        EPagination: PaginationStub,
        ESpinner: { name: 'ESpinner', template: '<div class="spinner" role="status" />' },
        EEmpty: { name: 'EEmpty', props: ['title'], template: '<div class="fallback-empty">{{ title }}</div>' },
      },
    },
  })
}

describe('PagedTable', () => {
  it('操作槽靠右，不进表格', () => {
    const wrapper = mount(PagedTable, {
      props: {
        columns: [{ key: 'name', title: '名称' }],
        data: [{ name: '甲' }],
        page: 1,
        pageSize: 20,
        total: 1,
      },
      slots: {
        actions: '<button class="create">新建</button>',
      },
      global: {
        stubs: {
          ETable: TableStub,
          EPagination: PaginationStub,
          ESpinner: { name: 'ESpinner', template: '<div class="spinner" />' },
          EEmpty: { name: 'EEmpty', template: '<div />' },
        },
      },
    })

    const button = wrapper.get('button.create')
    expect(button.element.parentElement?.className).toContain('ml-auto')
    expect(wrapper.find('.actions-leak').exists()).toBe(false)
  })

  it('顶栏按钮留在表格外，单元格插槽进表格', () => {
    const wrapper = mountList()

    expect(wrapper.find('button.query').exists()).toBe(true)
    expect(wrapper.find('.toolbar-leak').exists()).toBe(false)
    expect(wrapper.find('.cell-name').text()).toBe('甲')
    expect(wrapper.find('.paged-table-body').classes()).toContain('flex-1')
    expect(wrapper.find('.paged-table-body').classes()).toContain('min-w-0')
    expect(wrapper.find('.paged-table-body').classes()).toContain('max-w-full')
  })

  it('total 大于 0 时分页带默认每页条数', () => {
    const wrapper = mountList()
    const pager = wrapper.getComponent(PaginationStub)

    expect(pager.props('total')).toBe(80)
    expect(pager.props('pageSize')).toBe(50)
    expect(pager.props('pageSizes')).toEqual([20, 50, 100])
    expect(pager.props('showTotal')).toBe(true)
    expect(pager.props('showSizeChanger')).toBe(true)
  })

  it('省略每页条数时使用统一默认值 50', () => {
    const wrapper = mountList({ pageSize: undefined })
    expect(wrapper.getComponent(PaginationStub).props('pageSize')).toBe(50)
  })

  it('没有行时不渲染表格和列名，空态仍在', () => {
    const wrapper = mountList({ total: 0, data: [] })

    expect(wrapper.findComponent(PaginationStub).exists()).toBe(false)
    expect(wrapper.findComponent(TableStub).exists()).toBe(false)
    expect(wrapper.text()).not.toContain('名称')
    expect(wrapper.find('.empty-mark').text()).toBe('空')
    expect(wrapper.find('.paged-table-body').exists()).toBe(false)
    expect(wrapper.find('.paged-table-empty').classes()).toContain('flex-1')
  })

  it('加载中且没有行时只留加载圈', () => {
    const wrapper = mountList({ total: 0, data: [], loading: true })

    expect(wrapper.findComponent(TableStub).exists()).toBe(false)
    expect(wrapper.find('.empty-mark').exists()).toBe(false)
    expect(wrapper.find('.spinner').exists()).toBe(true)
  })

  it('没写空态时用暂无数据', () => {
    const wrapper = mount(PagedTable, {
      props: { columns: [{ key: 'name', title: '名称' }], data: [] },
      global: {
        stubs: {
          ETable: TableStub,
          EEmpty: { name: 'EEmpty', props: ['title'], template: '<div class="fallback-empty">{{ title }}</div>' },
        },
      },
    })

    expect(wrapper.findComponent(TableStub).exists()).toBe(false)
    expect(wrapper.find('.fallback-empty').text()).toBe('暂无数据')
  })

  it('不传 total 时不渲染分页', () => {
    const wrapper = mountList({ total: undefined })

    expect(wrapper.findComponent(PaginationStub).exists()).toBe(false)
  })

  it('翻页和改每页条数原样抛出', async () => {
    const wrapper = mountList()
    const pager = wrapper.getComponent(PaginationStub)

    await pager.vm.$emit('update:modelValue', 3)
    await pager.vm.$emit('update:pageSize', 100)

    expect(wrapper.emitted('update:page')?.[0]).toEqual([3])
    expect(wrapper.emitted('update:pageSize')?.[0]).toEqual([100])
  })

  it('表头排序和行点击原样抛出', async () => {
    const wrapper = mountList()
    const table = wrapper.getComponent(TableStub)

    await table.vm.$emit('sort', 'name', 'desc')
    await table.vm.$emit('row-click', { name: '甲' }, 0)

    expect(wrapper.emitted('sort')?.[0]).toEqual(['name', 'desc'])
    expect(wrapper.emitted('row-click')?.[0]).toEqual([{ name: '甲' }, 0])
  })

  it('fill 关掉时表格区不占满剩余高度', () => {
    const wrapper = mountList({ fill: false }, false)

    expect(wrapper.find('.paged-table-body').classes()).not.toContain('flex-1')
    expect(wrapper.find('button.query').exists()).toBe(false)
  })

  it('showTotal 可关', () => {
    const wrapper = mountList({ showTotal: false })

    expect(wrapper.getComponent(PaginationStub).props('showTotal')).toBe(false)
  })
})
