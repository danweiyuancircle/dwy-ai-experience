/** 使用正式 EUI 表格与分页，验证可见行、单元格插槽及翻页。 */
import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import { PagedTable } from '../../../src/components'

describe('PagedTable 正式 EUI 交互', () => {
  it('展示当前行并从真实分页按钮提交下一页', async () => {
    const wrapper = mount(PagedTable, {
      props: { columns: [{ key: 'name', title: '姓名' }], data: [{ id: 1, name: 'alice' }], page: 1, pageSize: 20, total: 60 },
      slots: { 'cell-name': '<strong>账户 alice</strong>' },
    })
    expect(wrapper.get('table').text()).toContain('账户 alice')
    const secondPage = wrapper.findAll('button').find((button) => button.text() === '2')
    expect(secondPage).toBeDefined()
    await secondPage!.trigger('click')
    expect(wrapper.emitted('update:page')).toEqual([[2]])
    wrapper.unmount()
  })

  it('真实横向溢出时提供提示和键盘滚动区，固定操作列保持透传', async () => {
    const wrapper = mount(PagedTable, {
      props: { columns: [{ key: 'name', title: '姓名' }, { key: 'action', title: '操作', width: 80, fixed: 'right' }], data: [{ id: 1, name: 'alice' }] },
      slots: { 'cell-action': '<button>详情</button>' },
    })
    const scroller = wrapper.get('[data-slot="table-container"]')
    expect(wrapper.find('[data-slot="table-scroll-hint"]').exists()).toBe(false)
    Object.defineProperties(scroller.element, {
      clientWidth: { value: 300, configurable: true },
      scrollWidth: { value: 900, configurable: true },
    })
    window.dispatchEvent(new Event('resize'))
    await wrapper.vm.$nextTick()
    expect(wrapper.get('[data-slot="table-scroll-hint"]').text()).toContain('左右滑动')
    expect(scroller.attributes('tabindex')).toBe('0')
    expect(scroller.attributes('aria-describedby')).toBe(wrapper.get('[data-slot="table-scroll-hint"]').attributes('id'))
    expect(wrapper.get('td:last-child').attributes('style')).toContain('right: 0px')
    wrapper.unmount()
  })
})
