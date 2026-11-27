/**
 * DataOverview：固定顺序，缺的段不渲染。
 */
import { defineComponent, h, markRaw } from 'vue'
import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import { createMemoryHistory, createRouter } from 'vue-router'
import { DataOverview } from '../../../src/components'

/** markRaw：放进概览数据后不再被包成响应式。 */
const Icon = markRaw(
  defineComponent({
    name: 'DemoIcon',
    setup() {
      return () => h('svg', { class: 'demo-icon' })
    },
  }),
)

/** 链接卡需要路由注入。 */
function mountOverview(props: Record<string, unknown>, slot = '') {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [{ path: '/:pathMatch(.*)*', component: { template: '<div />' } }],
  })
  return mount(DataOverview, {
    props,
    slots: slot ? { default: slot } : {},
    global: {
      plugins: [router],
      stubs: {
        ECard: defineComponent({
          name: 'ECard',
          template: '<div class="card"><slot /></div>',
        }),
        EStatistic: defineComponent({
          name: 'EStatistic',
          props: { title: String, value: [String, Number] },
          template: '<span class="stat">{{ title }} {{ value }}</span>',
        }),
      },
    },
  })
}

describe('DataOverview', () => {
  it('按无标题指标、分组、入口、插槽、说明排列', () => {
    const wrapper = mountOverview(
      {
        metrics: [{ title: '股票总数', value: 3 }],
        sections: [
          {
            title: '用户',
            columns: 5,
            metrics: [{ title: '正常用户', value: 8, to: '/users', icon: Icon }],
          },
        ],
        links: [{ title: 'API Key', description: '管理密钥', to: '/keys', icon: Icon }],
        note: '含今天',
      },
      '<p class="extra">日活</p>',
    )

    const text = wrapper.text()
    const grids = wrapper.findAll('[data-card-grid]')
    expect(grids).toHaveLength(3)
    expect(grids[1].classes()).toContain('@min-[72rem]:grid-cols-5')
    expect(grids[0].classes()).toEqual(grids[2].classes())
    expect(text.indexOf('股票总数')).toBeLessThan(text.indexOf('用户'))
    expect(text.indexOf('用户')).toBeLessThan(text.indexOf('API Key'))
    expect(text.indexOf('API Key')).toBeLessThan(text.indexOf('日活'))
    expect(text.indexOf('日活')).toBeLessThan(text.indexOf('含今天'))
    expect(wrapper.find('.demo-icon').exists()).toBe(true)
    expect(wrapper.find('a[href="/users"]').exists()).toBe(true)
    const cardOf = (title: string) => wrapper.findAll('.card').find((card) => card.text().includes(title))
    expect(cardOf('股票总数')?.find('.lucide-arrow-up-right').exists()).toBe(false)
    expect(cardOf('正常用户')?.find('.lucide-arrow-up-right').exists()).toBe(true)
    expect(cardOf('API Key')?.find('.lucide-arrow-up-right').exists()).toBe(true)
  })

  it('空的指标和入口不留空栅格', () => {
    const wrapper = mountOverview({ note: '' })

    expect(wrapper.find('[data-card-grid]').exists()).toBe(false)
    expect(wrapper.text()).toBe('')
  })
})
