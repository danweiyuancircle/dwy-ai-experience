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

  it('exports useToast from index', async () => {
    const { useToast } = await import('@/components/toast/index')
    expect(typeof useToast).toBe('function')
    const toast = useToast()
    // toast 本身可直接调用
    expect(typeof toast).toBe('function')
    // 也支持类型方法
    expect(typeof toast.success).toBe('function')
    expect(typeof toast.error).toBe('function')
    expect(typeof toast.warning).toBe('function')
    expect(typeof toast.info).toBe('function')
    expect(typeof toast.promise).toBe('function')
  })
})
