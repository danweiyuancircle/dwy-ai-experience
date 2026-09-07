import { defineComponent } from 'vue'
import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import { DEFAULT_MOBILE_BREAKPOINT, useEuiMobile } from '@/composables/useEuiMobile'
import { mockViewportWidth } from '../helpers/mock-viewport'

describe('useEuiMobile', () => {
  it('exports default breakpoint 767', () => {
    expect(DEFAULT_MOBILE_BREAKPOINT).toBe(767)
  })

  it('is true when viewport is at or below breakpoint', () => {
    mockViewportWidth(375)
    const Host = defineComponent({
      setup() {
        return { isMobile: useEuiMobile() }
      },
      template: '<div>{{ isMobile }}</div>',
    })
    const wrapper = mount(Host)
    expect(wrapper.text()).toBe('true')
  })

  it('is false when viewport is above breakpoint', () => {
    mockViewportWidth(1024)
    const Host = defineComponent({
      setup() {
        return { isMobile: useEuiMobile() }
      },
      template: '<div>{{ isMobile }}</div>',
    })
    const wrapper = mount(Host)
    expect(wrapper.text()).toBe('false')
  })

  it('respects an explicit breakpoint override', () => {
    mockViewportWidth(800)
    const Host = defineComponent({
      setup() {
        return { isMobile: useEuiMobile(900) }
      },
      template: '<div>{{ isMobile }}</div>',
    })
    const wrapper = mount(Host)
    expect(wrapper.text()).toBe('true')
  })
})
