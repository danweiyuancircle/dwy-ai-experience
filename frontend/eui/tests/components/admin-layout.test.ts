import { mount } from '@vue/test-utils'
import { describe, it, expect, vi } from 'vitest'
import EAdminLayout from '@/components/admin-layout/EAdminLayout.vue'

// Mock vue-router
vi.mock('vue-router', () => ({
  useRouter: () => ({ push: vi.fn() }),
  useRoute: () => ({ path: '/' }),
}))

describe('EAdminLayout', () => {
  it('renders with default props', () => {
    const wrapper = mount(EAdminLayout)
    expect(wrapper.find('[data-slot="admin-layout"]').exists()).toBe(true)
  })

  it('renders title prop', () => {
    const wrapper = mount(EAdminLayout, {
      props: { title: 'My App' },
    })
    expect(wrapper.text()).toContain('My App')
  })

  it('renders sidebar, header, and content slots', () => {
    const wrapper = mount(EAdminLayout, {
      slots: {
        default: '<div class="main-content">Main Content</div>',
        header: '<div class="header-content">Header</div>',
      },
    })
    expect(wrapper.find('[data-slot="admin-layout-sidebar"]').exists()).toBe(true)
    expect(wrapper.find('[data-slot="admin-layout-header"]').exists()).toBe(true)
    expect(wrapper.find('[data-slot="admin-layout-content"]').exists()).toBe(true)
    expect(wrapper.find('.main-content').text()).toBe('Main Content')
    expect(wrapper.find('.header-content').text()).toBe('Header')
  })

  it('hides footer by default', () => {
    const wrapper = mount(EAdminLayout)
    expect(wrapper.find('[data-slot="admin-layout-footer"]').exists()).toBe(false)
  })

  it('shows footer when showFooter is true', () => {
    const wrapper = mount(EAdminLayout, {
      props: { showFooter: true },
      slots: { footer: 'Copyright 2026' },
    })
    expect(wrapper.find('[data-slot="admin-layout-footer"]').exists()).toBe(true)
    expect(wrapper.text()).toContain('Copyright 2026')
  })

  it('emits update:collapsed when toggle button is clicked', async () => {
    const wrapper = mount(EAdminLayout, {
      props: { collapsed: false },
    })
    await wrapper.find('button').trigger('click')
    expect(wrapper.emitted('update:collapsed')?.[0]).toEqual([true])
  })
})
