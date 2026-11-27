/** 保留 App Cloud 既有概览卡出口，使用真实 EUI 与 RouterLink 验证展示和导航。 */
import { mount, flushPromises } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import { createMemoryHistory, createRouter } from 'vue-router'
import * as components from '../../../src/components'

describe('OverviewCard 兼容出口与正式 EUI 交互', () => {
  it('组件入口保留 OverviewCard，静态卡展示内容和图标但不伪装成链接', () => {
    expect(components).toHaveProperty('OverviewCard')
    const wrapper = mount(components.OverviewCard, {
      slots: { default: '<p>当前应用</p>', icon: '<span>应用图标</span>' },
    })
    expect(wrapper.text()).toContain('当前应用')
    expect(wrapper.text()).toContain('应用图标')
    expect(wrapper.find('a').exists()).toBe(false)
    wrapper.unmount()
  })

  it('提供 to 时通过真实 RouterLink 导航，并保留默认内容', async () => {
    expect(components).toHaveProperty('OverviewCard')
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/', component: { template: '<div />' } },
        { path: '/applications/adbox', component: { template: '<div />' } },
      ],
    })
    await router.push('/')
    await router.isReady()
    const wrapper = mount(components.OverviewCard, {
      props: { to: '/applications/adbox' },
      slots: { default: '<p>打开 ADBox</p>' },
      global: { plugins: [router] },
    })
    expect(wrapper.get('a').attributes('href')).toBe('/applications/adbox')
    expect(wrapper.text()).toContain('打开 ADBox')
    await wrapper.get('a').trigger('click')
    await flushPromises()
    expect(router.currentRoute.value.path).toBe('/applications/adbox')
    wrapper.unmount()
  })
})
