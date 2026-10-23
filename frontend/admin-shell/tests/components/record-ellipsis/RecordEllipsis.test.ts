/**
 * RecordEllipsis：空值和占位符不弹提示。
 */
import { defineComponent } from 'vue'
import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'
import { RecordEllipsis } from '../../../src/components'

const ETooltip = defineComponent({
  name: 'ETooltip',
  props: { content: String, disabled: Boolean, class: String },
  template: '<div class="tip" :data-disabled="String(disabled)" :data-content="content"><slot /></div>',
})

describe('RecordEllipsis', () => {
  it('完整可见文本不增加键盘停靠，截断时才可聚焦查看全文', async () => {
    const filled = mount(RecordEllipsis, {
      props: { text: 'alice@example.com', tooltipClass: 'w-fit' },
      global: { stubs: { ETooltip } },
    })
    const dash = mount(RecordEllipsis, {
      props: { text: '-', emptyText: '-' },
      global: { stubs: { ETooltip } },
    })
    const blank = mount(RecordEllipsis, {
      props: { text: '' },
      global: { stubs: { ETooltip } },
    })

    expect(filled.get('.tip').attributes('data-disabled')).toBe('true')
    expect(filled.get('span').attributes('tabindex')).toBeUndefined()
    // 提示层切换时可能重建触发节点，布局测量应对所有实际节点生效。
    const width = vi.spyOn(HTMLElement.prototype, 'clientWidth', 'get').mockReturnValue(80)
    const scrollWidth = vi.spyOn(HTMLElement.prototype, 'scrollWidth', 'get').mockReturnValue(200)
    window.dispatchEvent(new Event('resize'))
    await filled.vm.$nextTick()
    expect(filled.get('.tip').attributes('data-disabled')).toBe('false')
    expect(filled.get('span').attributes('tabindex')).toBe('0')
    expect(filled.get('.tip').attributes('data-content')).toBe('alice@example.com')
    expect(dash.get('.tip').attributes('data-disabled')).toBe('true')
    expect(dash.text()).toBe('-')
    expect(blank.text()).toBe('—')
    expect(blank.get('.tip').attributes('data-disabled')).toBe('true')
    width.mockReturnValue(240)
    window.dispatchEvent(new Event('resize'))
    await filled.vm.$nextTick()
    expect(filled.get('span').attributes('tabindex')).toBeUndefined()
    filled.unmount()
    dash.unmount()
    blank.unmount()
    width.mockRestore()
    scrollWidth.mockRestore()
  })
})
