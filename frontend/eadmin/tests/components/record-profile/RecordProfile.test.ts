/**
 * RecordProfile：返回和身份卡。没有标题时不画卡。
 */
import { defineComponent } from 'vue'
import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import { RecordProfile } from '../../../src/components'

const ECard = defineComponent({
  name: 'ECard',
  props: { title: { type: String, default: '' } },
  template: '<section class="card"><h3>{{ title }}</h3><slot /></section>',
})

const EButton = defineComponent({
  name: 'EButton',
  emits: ['click'],
  template: '<button class="back" type="button" @click="$emit(\'click\')"><slot /></button>',
})

describe('RecordProfile', () => {
  it('点返回向外抛，身份卡按标题、徽章、说明、操作排', async () => {
    const wrapper = mount(RecordProfile, {
      props: { title: 'alice', backLabel: '返回列表' },
      slots: {
        meta: '<span class="badge">正常</span>',
        description: 'a@x.com',
        actions: '<button class="act">禁用</button>',
        default: '<section class="bills">账单</section>',
      },
      global: { stubs: { ECard, EButton } },
    })

    expect(wrapper.get('.card h3').text()).toBe('alice')
    expect(wrapper.text()).toContain('正常')
    expect(wrapper.text()).toContain('a@x.com')
    expect(wrapper.text()).toContain('禁用')
    expect(wrapper.text()).toContain('账单')

    await wrapper.get('.back').trigger('click')
    expect(wrapper.emitted('back')).toHaveLength(1)
  })

  it('没有标题时不画身份卡，默认插槽仍在', () => {
    const wrapper = mount(RecordProfile, {
      props: { backLabel: '返回列表' },
      slots: { default: '<p class="empty">没有这个人</p>' },
      global: { stubs: { ECard, EButton } },
    })

    expect(wrapper.find('.card').exists()).toBe(false)
    expect(wrapper.text()).toContain('没有这个人')
    expect(wrapper.text()).toContain('返回列表')
  })
})
