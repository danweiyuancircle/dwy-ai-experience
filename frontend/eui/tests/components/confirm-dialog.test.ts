import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import EConfirmDialog from '@/components/confirm-dialog/EConfirmDialog.vue'

describe('EConfirmDialog', () => {
  it('renders without error when closed', () => {
    const wrapper = mount(EConfirmDialog, {
      props: { open: false },
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('renders without error when open', () => {
    const wrapper = mount(EConfirmDialog, {
      props: { open: true, title: 'Confirm', message: 'Are you sure?' },
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('accepts type prop', () => {
    const wrapper = mount(EConfirmDialog, {
      props: { open: false, type: 'warning' },
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('accepts custom confirm and cancel text', () => {
    const wrapper = mount(EConfirmDialog, {
      props: { open: false, confirmText: 'Yes', cancelText: 'No' },
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('renders portal content when open (dialog in DOM)', () => {
    const wrapper = mount(EConfirmDialog, {
      props: { open: true, title: 'Delete', message: 'Sure?' },
    })
    // DialogPortal teleports content to body; verify buttons exist in the document
    const buttons = document.querySelectorAll('button')
    expect(buttons.length).toBeGreaterThan(0)
    wrapper.unmount()
  })
})
