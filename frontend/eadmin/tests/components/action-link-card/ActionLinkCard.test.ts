/**
 * ActionLinkCard：整卡跳转。外壳与指标卡相同，箭头在图标井左侧。
 */
import { defineComponent, h } from 'vue'
import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import { createMemoryHistory, createRouter } from 'vue-router'
import { ActionLinkCard } from '../../../src/components'

describe('ActionLinkCard', () => {
  it('标题、说明和路径都在链接上', () => {
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [{ path: '/:pathMatch(.*)*', component: { template: '<div />' } }],
    })
    const wrapper = mount(ActionLinkCard, {
      props: { title: 'API Key', description: '管理密钥', to: '/keys' },
      slots: {
        icon: defineComponent({ setup: () => () => h('svg', { class: 'demo-icon' }) }),
      },
      global: { plugins: [router] },
    })

    expect(wrapper.attributes('href')).toBe('/keys')
    expect(wrapper.text()).toContain('API Key')
    expect(wrapper.text()).toContain('管理密钥')
    const card = wrapper.get('[data-slot="card"]')
    expect(card.classes()).toContain('group-hover:border-primary/40')
    expect(card.classes().join(' ')).not.toContain('hover:-translate')
    const well = wrapper.get('.demo-icon').element.parentElement
    expect(well?.className).toContain('size-10')
    expect(well?.className).toContain('rounded-lg')
    expect(well?.className).toContain('bg-primary/10')
    const arrow = wrapper.get('.lucide-arrow-up-right').element
    expect(arrow.compareDocumentPosition(wrapper.get('.demo-icon').element) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy()
  })
})
