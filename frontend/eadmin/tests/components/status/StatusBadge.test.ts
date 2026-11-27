/**
 * StatusBadge 与七档色。文案由页面传入。
 */
import { defineComponent } from 'vue'
import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import { StatusBadge, STATUS_TONE, completionClass, presenceClass } from '../../../src/components'

const EBadge = defineComponent({
  name: 'EBadge',
  props: { variant: String },
  template: '<span class="badge"><slot /></span>',
})

describe('StatusBadge', () => {
  it('用描边徽章加上对应档的类', () => {
    const wrapper = mount(StatusBadge, {
      props: { tone: 'active', label: '正常' },
      global: { stubs: { EBadge } },
    })

    expect(wrapper.text()).toBe('正常')
    expect(wrapper.get('.badge').classes()).toContain('font-normal')
    expect(wrapper.get('.badge').attributes('class')).toContain(STATUS_TONE.active)
  })

  it('开着和完成走生效色，关掉走停用色，未完成走待办色', () => {
    expect(presenceClass(true)).toBe(STATUS_TONE.active)
    expect(presenceClass(false)).toBe(STATUS_TONE.stopped)
    expect(completionClass(true)).toBe(STATUS_TONE.active)
    expect(completionClass(false)).toBe(STATUS_TONE.pending)
    expect(new Set(Object.values(STATUS_TONE)).size).toBe(7)
  })
})
