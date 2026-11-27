import { mount } from '@vue/test-utils'
import { defineComponent, h, nextTick, ref } from 'vue'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { ETransition } from '../../src'
import { EMotionList } from '../../src/motion'

afterEach(() => vi.unstubAllGlobals())

describe('EUI motion', () => {
  it('uses the chosen preset while retaining Vue conditional rendering', async () => {
    const visible = ref(true)
    const wrapper = mount(defineComponent({
      setup: () => () => h(ETransition, { preset: 'slide-up' }, () =>
        visible.value ? h('p', '已保存') : null,
      ),
    }))

    expect(wrapper.get('transition-stub').attributes('name')).toBe('eui-slide-up')
    expect(wrapper.get('p').text()).toBe('已保存')
    visible.value = false
    await nextTick()
    expect(wrapper.find('p').exists()).toBe(false)
  })

  it('keeps keyed item nodes when reduced-motion users reorder the list', async () => {
    vi.stubGlobal('matchMedia', () => ({ matches: true, addEventListener: vi.fn(), removeEventListener: vi.fn() }))
    const a = { id: 1, title: '新工单' }
    const b = { id: 2, title: '待审核' }
    const wrapper = mount(EMotionList, {
      attachTo: document.body,
      props: { items: [a, b], itemKey: 'id' },
      slots: { default: ({ item }) => h('button', (item as typeof a).title) },
    })
    try {
      const focused = wrapper.get('button').element
      focused.focus()
      await wrapper.setProps({ items: [b, a] })
      const buttons = wrapper.findAll('button')
      expect(buttons.map(button => button.text())).toEqual(['待审核', '新工单'])
      expect(buttons[1].element).toBe(focused)
      expect(document.activeElement).toBe(focused)
    } finally {
      wrapper.unmount()
    }
  })
})
