/** 使用正式 EUI 输入框和按钮验证用户提交路径，不以 stub 代替交互。 */
import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import { RecordSearch } from '../../../src/components'
import { defineComponent } from 'vue'

describe('RecordSearch 正式 EUI 交互', () => {
  it('输入更新关键词，回车与查询按钮均向页面提交', async () => {
    const wrapper = mount(RecordSearch, { props: { modelValue: '', placeholder: '用户名或邮箱', maxlength: 64 } })
    const input = wrapper.get('input')
    expect(input.attributes('maxlength')).toBe('64')
    await input.setValue('alice')
    expect(wrapper.emitted('update:modelValue')).toEqual([['alice']])
    await input.trigger('keydown', { key: 'Enter' })
    await wrapper.get('button').trigger('click')
    expect(wrapper.emitted('search')).toHaveLength(2)
    wrapper.unmount()
  })

  it('持久标签关联真实输入，不同实例使用独立 id', () => {
    const wrapper = mount(defineComponent({
      components: { RecordSearch },
      template: '<RecordSearch model-value="" label="查找用户" placeholder="用户名或邮箱" :maxlength="64" /><RecordSearch model-value="" placeholder="产品名称" :maxlength="64" />',
    }))
    const labels = wrapper.findAll('label')
    const inputs = wrapper.findAll('input')
    expect(labels[0]!.text()).toBe('查找用户')
    expect(labels[1]!.text()).toBe('产品名称')
    expect(labels[0]!.attributes('for')).toBe(inputs[0]!.attributes('id'))
    expect(labels[1]!.attributes('for')).toBe(inputs[1]!.attributes('id'))
    expect(inputs[0]!.attributes('id')).not.toBe(inputs[1]!.attributes('id'))
    wrapper.unmount()
  })

  it('清空按钮和手动删空都只提交一次空查询', async () => {
    const wrapper = mount(defineComponent({
      components: { RecordSearch },
      data: () => ({ keyword: 'alice', searches: 0 }),
      template: '<RecordSearch v-model="keyword" label="查找用户" placeholder="用户名或邮箱" :maxlength="64" @search="searches++" />',
    }))
    const search = wrapper.getComponent(RecordSearch)
    await wrapper.get('[data-slot="input-wrapper"] button').trigger('click')
    expect(search.emitted('clear')).toHaveLength(1)
    expect(search.emitted('search')).toHaveLength(1)
    await wrapper.get('input').setValue('bob')
    await wrapper.get('input').setValue('')
    expect(search.emitted('search')).toHaveLength(2)
    expect(search.emitted('clear')).toHaveLength(2)
    wrapper.unmount()
  })

  it('外部重置关键词不自行触发搜索请求', async () => {
    const wrapper = mount(RecordSearch, { props: { modelValue: 'alice', placeholder: '用户名或邮箱', maxlength: 64 } })
    await wrapper.setProps({ modelValue: '' })
    expect(wrapper.emitted('search')).toBeUndefined()
    expect(wrapper.emitted('clear')).toBeUndefined()
    wrapper.unmount()
  })

  it('输入法合成回车不提交，确认结束后的回车才提交', async () => {
    const wrapper = mount(RecordSearch, { props: { modelValue: '', placeholder: '用户名或邮箱', maxlength: 64 } })
    const input = wrapper.get('input')
    await input.trigger('compositionstart')
    await input.trigger('keydown', { key: 'Enter', isComposing: true })
    expect(wrapper.emitted('search')).toBeUndefined()
    await input.trigger('compositionend')
    await input.trigger('keydown', { key: 'Enter' })
    expect(wrapper.emitted('search')).toHaveLength(1)
    wrapper.unmount()
  })
})
