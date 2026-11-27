/**
 * RecordSearch：回车和按钮都只抛 search。
 */
import { defineComponent } from 'vue'
import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import { RecordSearch } from '../../../src/components'

const EInput = defineComponent({
  name: 'EInput',
  props: { modelValue: String, placeholder: String, maxlength: Number },
  emits: ['update:modelValue', 'keydown'],
  template:
    '<input class="field" :value="modelValue" :placeholder="placeholder" :maxlength="maxlength" @input="$emit(\'update:modelValue\', $event.target.value)" />',
})

const EButton = defineComponent({
  name: 'EButton',
  props: { loading: Boolean },
  template: '<button type="button" class="go"><slot /></button>',
})

describe('RecordSearch', () => {
  it('输入同步关键词，回车和按钮都触发查询', async () => {
    const wrapper = mount(RecordSearch, {
      props: { modelValue: '', placeholder: '用户名或邮箱', maxlength: 64, buttonText: '搜索' },
      global: { stubs: { EInput, EButton } },
    })

    await wrapper.get('.field').setValue('alice')
    expect(wrapper.emitted('update:modelValue')?.[0]).toEqual(['alice'])
    expect(wrapper.get('.field').attributes('maxlength')).toBe('64')

    await wrapper.getComponent(EInput).vm.$emit('keydown', { key: 'Enter' })
    await wrapper.get('.go').trigger('click')
    expect(wrapper.emitted('search')).toHaveLength(2)
    expect(wrapper.get('.go').text()).toBe('搜索')
  })
})
