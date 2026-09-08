import { flushPromises, mount } from '@vue/test-utils'
import { describe, it, expect, afterEach } from 'vitest'
import EFormDialog from '@/components/form-dialog/EFormDialog.vue'

describe('EFormDialog', () => {
  afterEach(() => {
    document.body.innerHTML = ''
  })

  it('renders without error when closed', () => {
    const wrapper = mount(EFormDialog, {
      props: { open: false },
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('renders without error when open', () => {
    const wrapper = mount(EFormDialog, {
      props: { open: true, title: 'Edit User' },
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('accepts title prop', () => {
    const wrapper = mount(EFormDialog, {
      props: { open: false, title: 'Create Item' },
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('accepts loading prop', () => {
    const wrapper = mount(EFormDialog, {
      props: { open: false, loading: true },
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('accepts custom button text props', () => {
    const wrapper = mount(EFormDialog, {
      props: { open: false, confirmText: 'Save', cancelText: 'Discard' },
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('accepts slot content', () => {
    const wrapper = mount(EFormDialog, {
      props: { open: false, title: 'Test' },
      slots: { default: '<p>Form fields</p>' },
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('打开时有 DialogDescription，避免 reka 缺 description 警告', async () => {
    const wrapper = mount(EFormDialog, {
      attachTo: document.body,
      props: { open: true, title: 'Edit User' },
    })
    await flushPromises()
    expect(document.querySelector('[data-slot="dialog-description"]')).not.toBeNull()
    wrapper.unmount()
  })
})
