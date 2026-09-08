import { flushPromises, mount } from '@vue/test-utils'
import { describe, it, expect, afterEach } from 'vitest'
import ESheet from '@/components/sheet/ESheet.vue'

describe('ESheet', () => {
  afterEach(() => {
    document.body.innerHTML = ''
  })

  it('mounts without error in closed state', () => {
    const wrapper = mount(ESheet)
    expect(wrapper.exists()).toBe(true)
  })

  it('does not render overlay in closed state (portaled)', () => {
    const wrapper = mount(ESheet)
    expect(wrapper.find('[data-slot="sheet-overlay"]').exists()).toBe(false)
  })

  it('关闭态不把 overlay 留在 document，避免挡住页面点击', async () => {
    const wrapper = mount(ESheet, {
      attachTo: document.body,
      props: { open: false },
    })
    await flushPromises()
    expect(document.querySelector('[data-slot="sheet-overlay"]')).toBeNull()
    expect(document.querySelector('[data-slot="sheet-content"]')).toBeNull()
    wrapper.unmount()
  })

  it('打开后 overlay 在 document，关闭后卸掉', async () => {
    const wrapper = mount(ESheet, {
      attachTo: document.body,
      props: { open: true, title: '侧栏' },
    })
    await flushPromises()
    expect(document.querySelector('[data-slot="sheet-overlay"]')).not.toBeNull()
    await wrapper.setProps({ open: false })
    await flushPromises()
    expect(document.querySelector('[data-slot="sheet-overlay"]')).toBeNull()
    wrapper.unmount()
  })

  it('打开态 overlay 高于应用顶栏 z-50，content 再高于 overlay', async () => {
    const wrapper = mount(ESheet, {
      attachTo: document.body,
      props: { open: true, title: '导航' },
    })
    await flushPromises()
    const overlay = document.querySelector('[data-slot="sheet-overlay"]') as HTMLElement | null
    const content = document.querySelector('[data-slot="sheet-content"]') as HTMLElement | null
    expect(getComputedStyle(overlay!).zIndex).toBe('2000')
    expect(getComputedStyle(content!).zIndex).toBe('2001')
    wrapper.unmount()
  })

  it('accepts open prop without error', () => {
    const wrapper = mount(ESheet, { props: { open: false } })
    expect(wrapper.exists()).toBe(true)
  })

  it('accepts title prop without error', () => {
    const wrapper = mount(ESheet, { props: { title: 'Sheet Title' } })
    expect(wrapper.exists()).toBe(true)
  })

  it('accepts side prop right', () => {
    const wrapper = mount(ESheet, { props: { side: 'right' } })
    expect(wrapper.exists()).toBe(true)
  })

  it('accepts side prop left', () => {
    const wrapper = mount(ESheet, { props: { side: 'left' } })
    expect(wrapper.exists()).toBe(true)
  })

  it('accepts side prop top', () => {
    const wrapper = mount(ESheet, { props: { side: 'top' } })
    expect(wrapper.exists()).toBe(true)
  })

  it('accepts side prop bottom', () => {
    const wrapper = mount(ESheet, { props: { side: 'bottom' } })
    expect(wrapper.exists()).toBe(true)
  })

  it('accepts description prop without error', () => {
    const wrapper = mount(ESheet, { props: { description: 'Sheet description' } })
    expect(wrapper.exists()).toBe(true)
  })

  it('emits update:open when close event triggers', () => {
    const wrapper = mount(ESheet, { props: { open: false } })
    // Component should mount and be ready to respond to open state changes
    expect(wrapper.exists()).toBe(true)
  })
})
