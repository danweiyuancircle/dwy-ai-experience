/**
 * StatCard：有路径整卡可点并带箭头，没有则只展示。
 * 外壳与入口卡相同：图标井在右侧。
 */
import { defineComponent, h } from 'vue'
import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import { createMemoryHistory, createRouter } from 'vue-router'
import { StatCard } from '../../../src/components'

const Icon = defineComponent({ setup: () => () => h('svg', { class: 'demo-icon' }) })

/** 右侧图标井。可点卡的箭头必须排在井的左边，井的右缘才对齐。 */
function iconWell(wrapper: ReturnType<typeof mount>) {
  return wrapper.get('.demo-icon').element.parentElement
}

describe('StatCard', () => {
  it('没有 to 时只展示，有 to 时是带箭头的链接', () => {
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [{ path: '/:pathMatch(.*)*', component: { template: '<div />' } }],
    })
    const plain = mount(StatCard, {
      props: { title: '股票总数', value: 1 },
      slots: { icon: Icon },
    })
    const linked = mount(StatCard, {
      props: { title: '因子总数', value: 2, to: '/factors' },
      slots: { icon: Icon },
      global: { plugins: [router] },
    })

    expect(plain.element.tagName).toBe('DIV')
    expect(plain.find('.lucide-arrow-up-right').exists()).toBe(false)
    expect(plain.get('[data-slot="card"]').classes().join(' ')).not.toContain('group-hover:')
    expect(iconWell(plain)?.className).toContain('size-10')
    expect(iconWell(plain)?.className).toContain('rounded-lg')
    expect(iconWell(plain)?.className).toContain('bg-primary/10')

    expect(linked.element.tagName).toBe('A')
    expect(linked.attributes('href')).toBe('/factors')
    expect(linked.get('[data-slot="card"]').classes()).toContain('group-hover:border-primary/40')
    const arrow = linked.get('.lucide-arrow-up-right').element
    const icon = linked.get('.demo-icon').element
    expect(arrow.compareDocumentPosition(icon) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy()
    expect(iconWell(linked)?.className).toBe(iconWell(plain)?.className)
  })
})
