import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import EDialog from '@/components/dialog/EDialog.vue'

describe('EDialog', () => {
  it('mounts without error in closed state', () => {
    const wrapper = mount(EDialog)
    expect(wrapper.exists()).toBe(true)
  })

  it('does not render trigger when slot is not provided', () => {
    const wrapper = mount(EDialog)
    expect(wrapper.find('[data-slot="dialog-trigger"]').exists()).toBe(false)
  })

  it('renders trigger slot with data-slot attribute', () => {
    const wrapper = mount(EDialog, {
      slots: { trigger: '<button>Open</button>' },
    })
    const trigger = wrapper.find('[data-slot="dialog-trigger"]')
    expect(trigger.exists()).toBe(true)
    expect(trigger.text()).toBe('Open')
  })

  it('trigger has aria-haspopup="dialog" and data-state="closed"', () => {
    const wrapper = mount(EDialog, {
      slots: { trigger: '<button>Open</button>' },
    })
    const trigger = wrapper.find('[data-slot="dialog-trigger"]')
    expect(trigger.attributes('aria-haspopup')).toBe('dialog')
    expect(trigger.attributes('data-state')).toBe('closed')
  })

  it('does not render overlay in closed state (portaled)', () => {
    const wrapper = mount(EDialog)
    expect(wrapper.find('[data-slot="dialog-overlay"]').exists()).toBe(false)
  })

  it('accepts open prop without error', () => {
    const wrapper = mount(EDialog, { props: { open: false } })
    expect(wrapper.exists()).toBe(true)
  })

  it('accepts title prop without error', () => {
    const wrapper = mount(EDialog, { props: { title: 'Test Title' } })
    expect(wrapper.exists()).toBe(true)
  })

  it('accepts description prop without error', () => {
    const wrapper = mount(EDialog, { props: { description: 'Test Description' } })
    expect(wrapper.exists()).toBe(true)
  })

  it('accepts fullscreen prop without error', () => {
    const wrapper = mount(EDialog, { props: { fullscreen: true } })
    expect(wrapper.exists()).toBe(true)
  })

  it('accepts draggable prop without error', () => {
    const wrapper = mount(EDialog, { props: { draggable: true } })
    expect(wrapper.exists()).toBe(true)
  })
})
