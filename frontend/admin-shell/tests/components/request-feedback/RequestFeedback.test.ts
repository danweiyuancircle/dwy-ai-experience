/** 使用正式 EUI 提示与按钮，验证请求失败重试及加载状态的可访问语义。 */
import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import { RequestFeedback } from '../../../src/components'

describe('RequestFeedback', () => {
  it('显示请求错误并通过重试按钮通知页面重新加载', async () => {
    const wrapper = mount(RequestFeedback, { props: { error: '服务暂时不可用' } })
    expect(wrapper.text()).toContain('服务暂时不可用')
    await wrapper.get('button').trigger('click')
    expect(wrapper.emitted('retry')).toEqual([[]])
    wrapper.unmount()
  })

  it('加载中提供可读状态，隐藏旧错误与重试入口', () => {
    const wrapper = mount(RequestFeedback, { props: { loading: true, error: '旧请求错误' } })
    expect(wrapper.get('[role="status"]').text()).toContain('正在加载')
    expect(wrapper.text()).not.toContain('旧请求错误')
    expect(wrapper.find('button').exists()).toBe(false)
    wrapper.unmount()
  })
})
