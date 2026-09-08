import { flushPromises, mount } from '@vue/test-utils'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import EAdminLayout from '@/components/admin-layout/EAdminLayout.vue'
import ESheet from '@/components/sheet/ESheet.vue'
import { mockViewportWidth } from '../helpers/mock-viewport'

// Mock vue-router
vi.mock('vue-router', () => ({
  useRouter: () => ({ push: vi.fn() }),
  useRoute: () => ({ path: '/' }),
}))

describe('EAdminLayout', () => {
  beforeEach(() => {
    mockViewportWidth(1024)
    document.body.innerHTML = ''
  })

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
    await wrapper.find('[data-slot="admin-layout-sidebar-trigger"]').trigger('click')
    expect(wrapper.emitted('update:collapsed')?.[0]).toEqual([true])
  })

  it('keeps docked sidebar on desktop', () => {
    const wrapper = mount(EAdminLayout)
    expect(wrapper.find('[data-slot="admin-layout-sidebar"]').exists()).toBe(true)
  })
})

describe('EAdminLayout mobile drawer', () => {
  beforeEach(() => {
    mockViewportWidth(375)
    document.body.innerHTML = ''
  })

  it('does not dock sidebar in the layout on mobile', () => {
    const wrapper = mount(EAdminLayout, { attachTo: document.body })
    const docked = wrapper.find('[data-slot="admin-layout"] > [data-slot="admin-layout-sidebar"]')
    expect(docked.exists()).toBe(false)
    wrapper.unmount()
  })

  it('emits update:mobileOpen when hamburger is clicked', async () => {
    const wrapper = mount(EAdminLayout, { attachTo: document.body })
    await wrapper.find('[data-slot="admin-layout-sidebar-trigger"]').trigger('click')
    await flushPromises()
    expect(wrapper.emitted('update:mobileOpen')?.[0]).toEqual([true])
    wrapper.unmount()
  })

  it('关闭态没有 sheet overlay，汉堡点击后抽屉真正出现', async () => {
    const wrapper = mount(EAdminLayout, {
      attachTo: document.body,
      props: { menuItems: [{ key: '/dash', label: '概览' }] },
    })
    await flushPromises()
    expect(document.querySelector('[data-slot="sheet-overlay"]')).toBeNull()
    const trigger = wrapper.find('[data-slot="admin-layout-sidebar-trigger"]')
    expect(trigger.exists()).toBe(true)
    await trigger.trigger('pointerdown')
    await trigger.trigger('click')
    await flushPromises()
    await new Promise((resolve) => setTimeout(resolve, 0))
    await wrapper.vm.$nextTick()
    expect(wrapper.emitted('update:mobileOpen')?.at(-1)).toEqual([true])
    expect(wrapper.findComponent(ESheet).props('open')).toBe(true)
    expect(document.querySelector('[data-slot="sheet-content"]')).not.toBeNull()
    wrapper.unmount()
  })

  it('汉堡点击后抽屉状态保持打开，不被同一手势立刻关掉', async () => {
    const wrapper = mount(EAdminLayout, {
      attachTo: document.body,
      props: { menuItems: [{ key: '/dash', label: '概览' }] },
    })
    const trigger = wrapper.find('[data-slot="admin-layout-sidebar-trigger"]')
    await trigger.trigger('pointerdown')
    await trigger.trigger('click')
    await flushPromises()
    await new Promise((resolve) => setTimeout(resolve, 0))
    expect(wrapper.emitted('update:mobileOpen')?.[0]).toEqual([true])
    expect(document.querySelector('[data-slot="sheet-content"]')).not.toBeNull()
    // 打开后再 pointerdown 汉堡：outside 被 ignore，不能自己关掉
    await trigger.trigger('pointerdown')
    await flushPromises()
    expect(wrapper.emitted('update:mobileOpen')?.at(-1)).toEqual([true])
    wrapper.unmount()
  })

  it('does not emit update:collapsed when hamburger is clicked on mobile', async () => {
    const wrapper = mount(EAdminLayout, {
      attachTo: document.body,
      props: { collapsed: false },
    })
    await wrapper.find('[data-slot="admin-layout-sidebar-trigger"]').trigger('click')
    expect(wrapper.emitted('update:collapsed')).toBeUndefined()
    wrapper.unmount()
  })

  it('renders sheet content when mobileOpen is true', async () => {
    const wrapper = mount(EAdminLayout, {
      attachTo: document.body,
      props: {
        mobileOpen: true,
        menuItems: [{ key: '/dash', label: '概览' }],
      },
    })
    await flushPromises()
    expect(document.querySelector('[data-slot="sheet-content"]')).not.toBeNull()
    wrapper.unmount()
  })

  it('closes sheet after menu select', async () => {
    const wrapper = mount(EAdminLayout, {
      attachTo: document.body,
      props: {
        mobileOpen: true,
        menuItems: [{ key: '/dash', label: '概览' }],
      },
    })
    await wrapper.vm.$nextTick()
    const item = document.querySelector('[data-slot="sheet-content"] [data-slot="menu-item"]')
      ?? document.querySelector('[data-slot="sheet-content"] button, [data-slot="sheet-content"] a')
    expect(item).not.toBeNull()
    item?.dispatchEvent(new MouseEvent('click', { bubbles: true }))
    await wrapper.vm.$nextTick()
    expect(wrapper.emitted('update:mobileOpen')?.at(-1)).toEqual([false])
    wrapper.unmount()
  })

  it('keeps docked sidebar when mobileMode is none', () => {
    const wrapper = mount(EAdminLayout, {
      props: { mobileMode: 'none' },
    })
    expect(wrapper.find('[data-slot="admin-layout-sidebar"]').exists()).toBe(true)
  })

  it('抽屉打开时顶栏 header 槽 hidden，避免用户名叠在关闭钮上', async () => {
    mockViewportWidth(375)
    const wrapper = mount(EAdminLayout, {
      attachTo: document.body,
      props: { mobileOpen: true },
      slots: { header: '<div class="header-content">用户名</div>' },
    })
    await flushPromises()
    const slotWrap = wrapper.find('.header-content').element.parentElement
    expect(slotWrap?.classList.contains('invisible')).toBe(true)
    wrapper.unmount()
  })

  it('抽屉打开时 content 叠在 overlay 之上，菜单可点', async () => {
    const wrapper = mount(EAdminLayout, {
      attachTo: document.body,
      props: {
        mobileOpen: true,
        menuItems: [{ key: '/dash', label: '概览' }],
      },
    })
    await flushPromises()
    const overlay = document.querySelector('[data-slot="sheet-overlay"]') as HTMLElement | null
    const content = document.querySelector('[data-slot="sheet-content"]') as HTMLElement | null
    expect(overlay).not.toBeNull()
    expect(content).not.toBeNull()
    // overlay 须压过应用顶栏 z-50；content 再高于 overlay，菜单可点
    expect(getComputedStyle(overlay!).zIndex).toBe('2000')
    expect(getComputedStyle(content!).zIndex).toBe('2001')
    // reka overlay 写死 inline pointer-events:auto，默认必须 !none，仅打开态 !auto
    expect(overlay?.className).toMatch(/!pointer-events-none/)
    expect(overlay?.className).toMatch(/data-\[state=open\]:!pointer-events-auto/)
    expect(content?.className).toMatch(/data-\[state=open\]:!pointer-events-auto/)
    wrapper.unmount()
  })
})

