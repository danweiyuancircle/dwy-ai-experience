import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import ENavigationMenu from '@/components/navigation-menu/ENavigationMenu.vue'

describe('ENavigationMenu', () => {
  it('renders with default props', () => {
    const wrapper = mount(ENavigationMenu, {
      slots: { default: '<div>nav items</div>' },
    })
    expect(wrapper.find('[data-slot="navigation-menu"]').exists()).toBe(true)
  })

  it('renders slot content', () => {
    const wrapper = mount(ENavigationMenu, {
      slots: { default: '<span class="nav-item">Link</span>' },
    })
    expect(wrapper.find('.nav-item').exists()).toBe(true)
    expect(wrapper.text()).toContain('Link')
  })

  it('has data-viewport attribute set to true by default', () => {
    const wrapper = mount(ENavigationMenu, {
      slots: { default: '<div>items</div>' },
    })
    const el = wrapper.find('[data-slot="navigation-menu"]')
    expect(el.attributes('data-viewport')).toBe('true')
  })

  it('has data-viewport attribute set to false when viewport is false', () => {
    const wrapper = mount(ENavigationMenu, {
      props: { viewport: false },
      slots: { default: '<div>items</div>' },
    })
    const el = wrapper.find('[data-slot="navigation-menu"]')
    expect(el.attributes('data-viewport')).toBe('false')
  })

  it('applies custom class', () => {
    const wrapper = mount(ENavigationMenu, {
      props: { class: 'my-nav' },
      slots: { default: '<div>items</div>' },
    })
    const el = wrapper.find('[data-slot="navigation-menu"]')
    expect(el.classes()).toContain('my-nav')
  })
})
