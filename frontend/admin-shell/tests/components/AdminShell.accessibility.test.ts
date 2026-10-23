/** 折叠后 logo 图标仍有完整首页链接名称。 */
import { defineComponent } from 'vue'
import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'
import { createMemoryHistory, createRouter } from 'vue-router'
import AdminShell from '../../src/components/AdminShell.vue'

vi.mock('@dwydev/ekit', async () => {
  const { ref } = await import('vue')
  return { useStorage: () => ref(true) }
})

describe('AdminShell 首页链接', () => {
  it('侧栏折叠时仍可读出系统名称和首页用途', async () => {
    const router = createRouter({ history: createMemoryHistory(), routes: [{ path: '/', component: { template: '<div />' } }] })
    await router.push('/')
    const wrapper = mount(AdminShell, {
      props: { title: '测试管理台', logo: '/logo.svg', menuItems: [], collapsedStorageKey: 'audit:collapsed' },
      global: {
        plugins: [router],
        stubs: {
          EAdminLayout: defineComponent({ template: '<div><slot name="logo" /><slot /></div>' }),
          AdminPageHero: true,
        },
      },
    })
    expect(wrapper.get('a').attributes('aria-label')).toBe('测试管理台首页')
    wrapper.unmount()
  })

  it.each(['/', ''])('未配置 logo 的折叠品牌区仍显示图标，logoTo=%s', async (logoTo) => {
    const router = createRouter({ history: createMemoryHistory(), routes: [{ path: '/', component: { template: '<div />' } }] })
    await router.push('/')
    const wrapper = mount(AdminShell, {
      props: { title: '测试管理台', logoTo, menuItems: [] },
      global: {
        plugins: [router],
        stubs: {
          EAdminLayout: defineComponent({ template: '<div><slot name="logo" /><slot /></div>' }),
          AdminPageHero: true,
        },
      },
    })
    expect(wrapper.find('svg').exists()).toBe(true)
    expect(wrapper.get('svg').attributes('aria-hidden')).toBe('true')
    expect(wrapper.get('svg').classes()).toContain('h-7')
    if (logoTo) expect(wrapper.get('a').attributes('aria-label')).toBe('测试管理台首页')
    else expect(wrapper.find('a').exists()).toBe(false)
    wrapper.unmount()
  })
})
