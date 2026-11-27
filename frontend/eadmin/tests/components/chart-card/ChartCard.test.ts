/**
 * ChartCard：标题右侧放切换，说明在图上方。
 */
import { defineComponent } from 'vue'
import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import { ChartCard } from '../../../src/components'

const ECard = defineComponent({
  name: 'ECard',
  props: { title: String },
  template: '<section><h2>{{ title }}</h2><div class="extra"><slot name="title-extra" /></div><slot /></section>',
})

describe('ChartCard', () => {
  it('有说明和右侧插槽时都渲染', () => {
    const wrapper = mount(ChartCard, {
      props: { title: '用户增长', description: '含今天' },
      slots: { extra: '<button class="days">近 7 天</button>', default: '<div class="plot" />' },
      global: { stubs: { ECard } },
    })

    expect(wrapper.get('h2').text()).toBe('用户增长')
    expect(wrapper.get('.extra').text()).toContain('近 7 天')
    expect(wrapper.text()).toContain('含今天')
    expect(wrapper.find('.plot').exists()).toBe(true)
  })

  it('没写说明和右侧时不留空位', () => {
    const wrapper = mount(ChartCard, {
      props: { title: '每日日活' },
      global: { stubs: { ECard } },
    })

    expect(wrapper.find('.extra').text()).toBe('')
    expect(wrapper.find('p').exists()).toBe(false)
  })
})
