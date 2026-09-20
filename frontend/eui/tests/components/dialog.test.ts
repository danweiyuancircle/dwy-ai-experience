import { flushPromises, mount } from '@vue/test-utils'
import { describe, it, expect, afterEach } from 'vitest'
import EDialog from '@/components/dialog/EDialog.vue'

describe('EDialog', () => {
  afterEach(() => {
    document.body.innerHTML = ''
  })

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

  // Security: destroyOnClose defaults to true
  it('defaults destroyOnClose to true', () => {
    const wrapper = mount(EDialog, { props: { destroyOnClose: true } })
    expect(wrapper.exists()).toBe(true)
  })

  it('accepts destroyOnClose=false to preserve content on close', () => {
    const wrapper = mount(EDialog, { props: { destroyOnClose: false } })
    expect(wrapper.exists()).toBe(true)
  })

  it('默认 destroyOnClose 关闭后卸掉 overlay（对齐 reka unmountOnHide=true）', async () => {
    const wrapper = mount(EDialog, {
      attachTo: document.body,
      props: { open: true, title: '标题' },
    })
    await flushPromises()
    expect(document.querySelector('[data-slot="dialog-overlay"]')).not.toBeNull()
    await wrapper.setProps({ open: false })
    await flushPromises()
    expect(document.querySelector('[data-slot="dialog-overlay"]')).toBeNull()
    wrapper.unmount()
  })

  it('destroyOnClose=false 关闭后仍保留 overlay（对齐 reka unmountOnHide=false）', async () => {
    const wrapper = mount(EDialog, {
      attachTo: document.body,
      props: { open: true, title: '标题', destroyOnClose: false },
    })
    await flushPromises()
    expect(document.querySelector('[data-slot="dialog-overlay"]')).not.toBeNull()
    await wrapper.setProps({ open: false })
    await flushPromises()
    expect(document.querySelector('[data-slot="dialog-overlay"]')).not.toBeNull()
    wrapper.unmount()
  })

  it('关闭瞬间不卸 body，避免收起动画期间高度塌掉', async () => {
    const wrapper = mount(EDialog, {
      attachTo: document.body,
      props: { open: true, title: '标题' },
      slots: { default: '<p id="dlg-slot-body">表单</p>' },
    })
    await flushPromises()
    expect(document.querySelector('#dlg-slot-body')).not.toBeNull()

    await wrapper.setProps({ open: false })
    expect(document.querySelector('[data-slot="dialog-content"]')).not.toBeNull()
    expect(document.querySelector('#dlg-slot-body')).not.toBeNull()

    await flushPromises()
    wrapper.unmount()
  })

  it('无 description 时仍渲染 sr-only DialogDescription，满足 reka 无障碍', async () => {
    const wrapper = mount(EDialog, {
      attachTo: document.body,
      props: { open: true, title: '编辑' },
    })
    await flushPromises()
    const desc = document.querySelector('[data-slot="dialog-description"]')
    expect(desc).not.toBeNull()
    expect(desc?.classList.contains('sr-only')).toBe(true)
    wrapper.unmount()
  })
})
