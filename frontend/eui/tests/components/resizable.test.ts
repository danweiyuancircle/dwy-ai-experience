import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import EResizablePanelGroup from '@/components/resizable/EResizablePanelGroup.vue'

describe('EResizablePanelGroup', () => {
  it('renders with default props', () => {
    const wrapper = mount(EResizablePanelGroup, {
      slots: { default: '<div>panels</div>' },
    })
    expect(wrapper.find('[data-slot="resizable-panel-group"]').exists()).toBe(true)
  })

  it('renders slot content', () => {
    const wrapper = mount(EResizablePanelGroup, {
      slots: { default: '<span class="panel">Panel A</span>' },
    })
    expect(wrapper.find('.panel').exists()).toBe(true)
    expect(wrapper.text()).toContain('Panel A')
  })

  it('defaults to horizontal direction', () => {
    const wrapper = mount(EResizablePanelGroup, {
      slots: { default: '<div>panels</div>' },
    })
    const el = wrapper.find('[data-slot="resizable-panel-group"]')
    expect(el.attributes('data-orientation')).toBe('horizontal')
  })

  it('supports vertical direction', () => {
    const wrapper = mount(EResizablePanelGroup, {
      props: { direction: 'vertical' },
      slots: { default: '<div>panels</div>' },
    })
    const el = wrapper.find('[data-slot="resizable-panel-group"]')
    expect(el.attributes('data-orientation')).toBe('vertical')
  })

  it('applies custom class', () => {
    const wrapper = mount(EResizablePanelGroup, {
      props: { class: 'my-resizable' },
      slots: { default: '<div>panels</div>' },
    })
    const el = wrapper.find('[data-slot="resizable-panel-group"]')
    expect(el.classes()).toContain('my-resizable')
  })
})
