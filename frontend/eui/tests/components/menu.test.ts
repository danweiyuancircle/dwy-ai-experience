import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import EMenu from '@/components/menu/EMenu.vue'

const baseItems = [
  { key: 'home', label: 'Home' },
  { key: 'about', label: 'About' },
  { key: 'settings', label: 'Settings', disabled: true },
]

const nestedItems = [
  {
    key: 'nav',
    label: 'Navigation',
    children: [
      { key: 'nav-1', label: 'Sub Item 1' },
      { key: 'nav-2', label: 'Sub Item 2' },
    ],
  },
  { key: 'home', label: 'Home' },
]

describe('EMenu', () => {
  it('renders a nav element by default', () => {
    const wrapper = mount(EMenu)
    expect(wrapper.find('nav').exists()).toBe(true)
    expect(wrapper.find('[data-slot="menu"]').exists()).toBe(true)
  })

  it('renders menu items from items prop', () => {
    const wrapper = mount(EMenu, { props: { items: baseItems } })
    const buttons = wrapper.findAll('button')
    // 3 flat items → 3 buttons
    expect(buttons.length).toBe(3)
    expect(wrapper.text()).toContain('Home')
    expect(wrapper.text()).toContain('About')
    expect(wrapper.text()).toContain('Settings')
  })

  it('applies collapsed width class when collapsed prop is true', () => {
    const wrapper = mount(EMenu, {
      props: { items: baseItems, collapsed: true },
    })
    const nav = wrapper.find('nav')
    expect(nav.classes()).toContain('w-14')
  })

  it('applies default width class when not collapsed', () => {
    const wrapper = mount(EMenu, {
      props: { items: baseItems, collapsed: false },
    })
    const nav = wrapper.find('nav')
    expect(nav.classes()).toContain('w-56')
  })

  it('marks disabled items with disabled attribute', () => {
    const wrapper = mount(EMenu, { props: { items: baseItems } })
    const buttons = wrapper.findAll('button')
    const disabledBtn = buttons.find((b) => b.text().includes('Settings'))
    expect(disabledBtn?.attributes('disabled')).toBeDefined()
  })

  it('emits select and update:modelValue on item click', async () => {
    const wrapper = mount(EMenu, { props: { items: baseItems } })
    const homeBtn = wrapper.findAll('button').find((b) => b.text().includes('Home'))!
    await homeBtn.trigger('click')
    expect(wrapper.emitted('select')?.[0]).toEqual(['home'])
    expect(wrapper.emitted('update:modelValue')?.[0]).toEqual(['home'])
  })

  it('highlights active item based on modelValue', () => {
    const wrapper = mount(EMenu, {
      props: { items: baseItems, modelValue: 'about' },
    })
    const aboutBtn = wrapper.findAll('button').find((b) => b.text().includes('About'))!
    expect(aboutBtn.classes().join(' ')).toContain('bg-primary')
  })

  it('hides labels in collapsed mode', () => {
    const wrapper = mount(EMenu, {
      props: { items: baseItems, collapsed: true },
    })
    // In collapsed mode, span with label text is not rendered (v-if="!collapsed")
    const spans = wrapper.findAll('span')
    expect(spans.length).toBe(0)
  })

  it('renders nested items as collapsible when not collapsed', () => {
    const wrapper = mount(EMenu, {
      props: { items: nestedItems, collapsed: false },
    })
    // The parent item "Navigation" should appear as a collapsible trigger
    expect(wrapper.text()).toContain('Navigation')
    // Flat item
    expect(wrapper.text()).toContain('Home')
  })
})
