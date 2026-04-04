import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import ESidebarProvider from '@/components/sidebar/ESidebarProvider.vue'

describe('ESidebarProvider', () => {
  it('renders with default props', () => {
    const wrapper = mount(ESidebarProvider, {
      slots: { default: '<div>sidebar content</div>' },
    })
    expect(wrapper.find('[data-slot="sidebar-wrapper"]').exists()).toBe(true)
  })

  it('renders slot content', () => {
    const wrapper = mount(ESidebarProvider, {
      slots: { default: '<span class="test-child">Hello</span>' },
    })
    expect(wrapper.find('.test-child').exists()).toBe(true)
    expect(wrapper.text()).toContain('Hello')
  })

  it('applies custom class', () => {
    const wrapper = mount(ESidebarProvider, {
      props: { class: 'my-sidebar-provider' },
      slots: { default: '<div>content</div>' },
    })
    const el = wrapper.find('[data-slot="sidebar-wrapper"]')
    expect(el.classes()).toContain('my-sidebar-provider')
  })

  it('sets sidebar CSS variables', () => {
    const wrapper = mount(ESidebarProvider, {
      slots: { default: '<div>content</div>' },
    })
    const el = wrapper.find('[data-slot="sidebar-wrapper"]')
    expect(el.attributes('style')).toContain('--sidebar-width')
    expect(el.attributes('style')).toContain('--sidebar-width-icon')
  })
})
