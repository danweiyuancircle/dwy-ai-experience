import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import ETextarea from '@/components/textarea/ETextarea.vue'

describe('ETextarea', () => {
  it('默认渲染 textarea 元素', () => {
    const wrapper = mount(ETextarea)
    expect(wrapper.find('textarea').exists()).toBe(true)
  })

  it('v-model 双向绑定', async () => {
    const wrapper = mount(ETextarea, {
      props: {
        modelValue: 'hello',
        'onUpdate:modelValue': (val: string) => wrapper.setProps({ modelValue: val }),
      },
    })
    const textarea = wrapper.find('textarea')
    expect(textarea.element.value).toBe('hello')

    await textarea.setValue('world')
    expect(wrapper.props('modelValue')).toBe('world')
  })

  it('placeholder prop', () => {
    const wrapper = mount(ETextarea, {
      props: { placeholder: '请输入内容' },
    })
    expect(wrapper.find('textarea').attributes('placeholder')).toBe('请输入内容')
  })

  it('disabled prop', () => {
    const wrapper = mount(ETextarea, {
      props: { disabled: true },
    })
    expect(wrapper.find('textarea').element.disabled).toBe(true)
  })

  it('readonly prop', () => {
    const wrapper = mount(ETextarea, {
      props: { readonly: true },
    })
    expect(wrapper.find('textarea').element.readOnly).toBe(true)
  })

  it('rows prop', () => {
    const wrapper = mount(ETextarea, {
      props: { rows: 6 },
    })
    expect(wrapper.find('textarea').attributes('rows')).toBe('6')
  })

  it('maxlength prop', () => {
    const wrapper = mount(ETextarea, {
      props: { maxlength: 100 },
    })
    expect(wrapper.find('textarea').attributes('maxlength')).toBe('100')
  })

  it('showWordLimit 显示字数统计', () => {
    const wrapper = mount(ETextarea, {
      props: { modelValue: 'abc', maxlength: 10, showWordLimit: true },
    })
    expect(wrapper.text()).toContain('3/10')
  })
})
