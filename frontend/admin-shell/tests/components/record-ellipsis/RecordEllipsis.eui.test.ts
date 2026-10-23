/** 正式 EUI 提示层不会把完整文本变成多余键盘停靠。 */
import { flushPromises, mount } from '@vue/test-utils'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { defineComponent } from 'vue'
import { RecordEllipsis } from '../../../src/components'

describe('RecordEllipsis 正式 EUI', () => {
  afterEach(() => {
    vi.restoreAllMocks()
    vi.unstubAllGlobals()
  })
  it('仅真实截断文本提供键盘焦点，仍保留完整文本供辅助技术读取', async () => {
    const wrapper = mount(RecordEllipsis, { props: { text: '较长的用户说明' } })
    const text = wrapper.get('span.truncate')
    expect(text.attributes('tabindex')).toBeUndefined()
    Object.defineProperties(text.element, {
      clientWidth: { value: 40 },
      scrollWidth: { value: 200 },
    })
    window.dispatchEvent(new Event('resize'))
    await wrapper.vm.$nextTick()
    expect(text.attributes('tabindex')).toBe('0')
    expect(text.text()).toBe('较长的用户说明')
    wrapper.unmount()
  })

  it.each(['Enter', ' '])('窄屏用 %s 打开全文，不误触父级行操作', async (key) => {
    vi.stubGlobal('matchMedia', vi.fn((query: string) => ({
      matches: query.includes('max-width'), media: query, onchange: null,
      addEventListener() {}, removeEventListener() {}, addListener() {}, removeListener() {},
      dispatchEvent: () => true,
    })))
    vi.spyOn(HTMLElement.prototype, 'clientWidth', 'get').mockReturnValue(40)
    vi.spyOn(HTMLElement.prototype, 'scrollWidth', 'get').mockReturnValue(200)
    const onRowClick = vi.fn()
    const wrapper = mount(defineComponent({
      components: { RecordEllipsis },
      setup: () => ({ onRowClick }),
      template: '<div @click="onRowClick"><RecordEllipsis text="较长的用户说明" /></div>',
    }), { attachTo: document.body })
    await flushPromises()
    const trigger = wrapper.get('span.truncate')
    await trigger.trigger('keydown', { key })
    await flushPromises()
    expect(trigger.attributes('data-state')).toBe('open')
    expect(document.querySelector('[data-slot="tooltip-content"]')?.textContent).toBe('较长的用户说明')
    expect(onRowClick).not.toHaveBeenCalled()
    wrapper.unmount()
  })
})
