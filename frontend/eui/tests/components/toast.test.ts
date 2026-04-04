import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import EToast from '@/components/toast/EToast.vue'

describe('EToast', () => {
  it('renders without error', () => {
    const wrapper = mount(EToast)
    expect(wrapper.exists()).toBe(true)
  })

  it('accepts position prop', () => {
    const wrapper = mount(EToast, {
      props: { position: 'top-right' },
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('accepts richColors prop', () => {
    const wrapper = mount(EToast, {
      props: { richColors: true },
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('exports toast function from index', async () => {
    const { toast } = await import('@/components/toast/index')
    expect(typeof toast).toBe('function')
  })
})
