/** 使用正式 EUI 控件验证文本长度与布尔值交互的边界。 */
import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import { ConfigFieldControl } from '../../../src/components'

describe('ConfigFieldControl 正式 EUI 交互', () => {
  it('字符串输入保留上限并写回当前值', async () => {
    const wrapper = mount(ConfigFieldControl, { props: { modelValue: '', spec: { kind: 'string', maxLength: 32 } } })
    expect(wrapper.get('input').attributes('maxlength')).toBe('32')
    await wrapper.get('input').setValue('示例配置')
    expect(wrapper.emitted('update:modelValue')).toEqual([['示例配置']])
    wrapper.unmount()
  })

  it('开关通过真实点击写回布尔值', async () => {
    const wrapper = mount(ConfigFieldControl, { props: { modelValue: false, spec: { kind: 'bool' } } })
    await wrapper.get('[role="switch"]').trigger('click')
    expect(wrapper.emitted('update:modelValue')).toEqual([[true]])
    wrapper.unmount()
  })
})
