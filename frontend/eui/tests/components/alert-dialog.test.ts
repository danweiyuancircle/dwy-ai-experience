import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import EAlertDialog from '@/components/alert-dialog/EAlertDialog.vue'

describe('EAlertDialog', () => {
  it('mounts without error in closed state', () => {
    const wrapper = mount(EAlertDialog)
    expect(wrapper.exists()).toBe(true)
  })

  it('does not render overlay in closed state (portaled)', () => {
    const wrapper = mount(EAlertDialog)
    expect(wrapper.find('[data-slot="alert-dialog-overlay"]').exists()).toBe(false)
  })

  it('accepts open prop without error', () => {
    const wrapper = mount(EAlertDialog, { props: { open: false } })
    expect(wrapper.exists()).toBe(true)
  })

  it('accepts title prop without error', () => {
    const wrapper = mount(EAlertDialog, { props: { title: 'Are you sure?' } })
    expect(wrapper.exists()).toBe(true)
  })

  it('accepts description prop without error', () => {
    const wrapper = mount(EAlertDialog, {
      props: { description: 'This action cannot be undone.' },
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('accepts custom confirmText and cancelText', () => {
    const wrapper = mount(EAlertDialog, {
      props: { confirmText: 'Delete', cancelText: 'Go back' },
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('renders trigger slot content when provided', () => {
    const wrapper = mount(EAlertDialog, {
      slots: { trigger: '<button>Delete</button>' },
    })
    expect(wrapper.text()).toContain('Delete')
  })

  it('does not render content in closed state', () => {
    const wrapper = mount(EAlertDialog, {
      props: { title: 'Confirm', description: 'Are you sure?' },
    })
    expect(wrapper.find('[data-slot="alert-dialog-content"]').exists()).toBe(false)
  })
})
