import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import EMenubar from '@/components/menubar/EMenubar.vue'

describe('EMenubar', () => {
  it('renders with default props', () => {
    const wrapper = mount(EMenubar, {
      slots: { default: '<div>menus</div>' },
    })
    expect(wrapper.find('[data-slot="menubar"]').exists()).toBe(true)
  })

  it('renders slot content', () => {
    const wrapper = mount(EMenubar, {
      slots: { default: '<span class="menu-item">File</span>' },
    })
    expect(wrapper.find('.menu-item').exists()).toBe(true)
    expect(wrapper.text()).toContain('File')
  })

  it('applies custom class', () => {
    const wrapper = mount(EMenubar, {
      props: { class: 'my-menubar' },
      slots: { default: '<div>menus</div>' },
    })
    const el = wrapper.find('[data-slot="menubar"]')
    expect(el.classes()).toContain('my-menubar')
  })

  it('has data-slot attribute', () => {
    const wrapper = mount(EMenubar, {
      slots: { default: '<div>menus</div>' },
    })
    expect(wrapper.find('[data-slot="menubar"]').attributes('data-slot')).toBe('menubar')
  })
})
