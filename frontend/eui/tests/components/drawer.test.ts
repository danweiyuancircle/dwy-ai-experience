import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import EDrawer from '@/components/drawer/EDrawer.vue'

describe('EDrawer', () => {
  it('mounts without error in closed state', () => {
    const wrapper = mount(EDrawer)
    expect(wrapper.exists()).toBe(true)
  })

  it('does not render trigger when slot is not provided', () => {
    const wrapper = mount(EDrawer)
    expect(wrapper.find('[data-slot="drawer-trigger"]').exists()).toBe(false)
  })

  it('renders trigger slot with data-slot attribute', () => {
    const wrapper = mount(EDrawer, {
      slots: { trigger: '<button>Open Drawer</button>' },
    })
    const trigger = wrapper.find('[data-slot="drawer-trigger"]')
    expect(trigger.exists()).toBe(true)
    expect(trigger.text()).toBe('Open Drawer')
  })

  it('trigger has data-state="closed" when drawer is closed', () => {
    const wrapper = mount(EDrawer, {
      slots: { trigger: '<button>Open</button>' },
    })
    const trigger = wrapper.find('[data-slot="drawer-trigger"]')
    expect(trigger.attributes('data-state')).toBe('closed')
  })

  it('does not render overlay in closed state (portaled)', () => {
    const wrapper = mount(EDrawer)
    expect(wrapper.find('[data-slot="drawer-overlay"]').exists()).toBe(false)
  })

  it('accepts open prop without error', () => {
    const wrapper = mount(EDrawer, { props: { open: false } })
    expect(wrapper.exists()).toBe(true)
  })

  it('accepts title prop without error', () => {
    const wrapper = mount(EDrawer, { props: { title: 'Drawer Title' } })
    expect(wrapper.exists()).toBe(true)
  })

  it('accepts direction prop right', () => {
    const wrapper = mount(EDrawer, { props: { direction: 'right' } })
    expect(wrapper.exists()).toBe(true)
  })

  it('accepts direction prop left', () => {
    const wrapper = mount(EDrawer, { props: { direction: 'left' } })
    expect(wrapper.exists()).toBe(true)
  })

  it('accepts direction prop top', () => {
    const wrapper = mount(EDrawer, { props: { direction: 'top' } })
    expect(wrapper.exists()).toBe(true)
  })

  // Security: destroyOnClose
  it('accepts destroyOnClose prop without error', () => {
    const wrapper = mount(EDrawer, { props: { destroyOnClose: true } })
    expect(wrapper.exists()).toBe(true)
  })

  it('accepts destroyOnClose=false to preserve content on close', () => {
    const wrapper = mount(EDrawer, { props: { destroyOnClose: false } })
    expect(wrapper.exists()).toBe(true)
  })
})
