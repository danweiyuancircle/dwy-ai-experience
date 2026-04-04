import { mount } from '@vue/test-utils'
import { describe, it, expect, beforeAll } from 'vitest'
import EScrollArea from '@/components/scroll-area/EScrollArea.vue'

beforeAll(() => {
  // ScrollArea uses ResizeObserver internally via reka-ui
  if (!globalThis.ResizeObserver) {
    globalThis.ResizeObserver = class {
      observe() {}
      unobserve() {}
      disconnect() {}
    } as unknown as typeof ResizeObserver
  }
})

describe('EScrollArea', () => {
  it('renders a scroll area root element', () => {
    const wrapper = mount(EScrollArea)
    expect(wrapper.find('[data-slot="scroll-area"]').exists()).toBe(true)
  })

  it('renders viewport element', () => {
    const wrapper = mount(EScrollArea)
    expect(wrapper.find('[data-slot="scroll-area-viewport"]').exists()).toBe(true)
  })

  it('renders slot content inside viewport', () => {
    const wrapper = mount(EScrollArea, {
      slots: {
        default: '<div class="scroll-content">Scrollable content here</div>',
      },
    })
    expect(wrapper.find('.scroll-content').exists()).toBe(true)
    expect(wrapper.text()).toContain('Scrollable content here')
  })

  it('has relative positioning on root', () => {
    const wrapper = mount(EScrollArea)
    const root = wrapper.find('[data-slot="scroll-area"]')
    expect(root.classes()).toContain('relative')
  })

  it('applies custom class to root element', () => {
    const wrapper = mount(EScrollArea, {
      props: { class: 'my-scroll-area' },
    })
    const root = wrapper.find('[data-slot="scroll-area"]')
    expect(root.classes()).toContain('my-scroll-area')
  })

  it('accepts type prop without error', () => {
    const wrapper = mount(EScrollArea, {
      props: { type: 'always' },
    })
    expect(wrapper.find('[data-slot="scroll-area"]').exists()).toBe(true)
  })
})
