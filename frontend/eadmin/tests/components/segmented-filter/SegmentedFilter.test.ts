/**
 * SegmentedFilter：空值不向外抛；计数跟在文案后。
 */
import { defineComponent, h } from 'vue'
import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import { SegmentedFilter } from '../../../src/components'

const EToggleGroup = defineComponent({
  name: 'EToggleGroup',
  props: { modelValue: String },
  emits: ['update:modelValue'],
  setup(_, { slots, emit }) {
    return () =>
      h('div', [
        h('button', { class: 'pick', onClick: () => emit('update:modelValue', '7') }, '7'),
        h('button', { class: 'clear', onClick: () => emit('update:modelValue', '') }, 'clear'),
        slots.default?.(),
      ])
  },
})

const EToggleGroupItem = defineComponent({
  name: 'EToggleGroupItem',
  props: { value: String },
  template: '<span class="item"><slot /></span>',
})

describe('SegmentedFilter', () => {
  it('选中新档才抛出，取消选中被忽略', async () => {
    const wrapper = mount(SegmentedFilter, {
      props: {
        modelValue: '30',
        options: [
          { label: '近 7 天', value: '7' },
          { label: '近 30 天', value: '30' },
        ],
      },
      global: { stubs: { EToggleGroup, EToggleGroupItem } },
    })

    await wrapper.get('.pick').trigger('click')
    expect(wrapper.emitted('update:modelValue')).toEqual([['7']])

    await wrapper.get('.clear').trigger('click')
    expect(wrapper.emitted('update:modelValue')).toEqual([['7']])
  })

  it('有计数时跟在文案后，0 也显示，并画出左侧名字', () => {
    const wrapper = mount(SegmentedFilter, {
      props: {
        modelValue: 'active',
        label: '状态',
        options: [
          { label: '正常', value: 'active', count: 0 },
          { label: '已禁用', value: 'disabled', count: 3 },
        ],
      },
      global: { stubs: { EToggleGroup, EToggleGroupItem } },
    })

    expect(wrapper.text()).toContain('状态')
    expect(wrapper.text()).toContain('正常 0')
    expect(wrapper.text()).toContain('已禁用 3')
    // 选中态必须盖过 accent：筛选条底是 muted，accent 与底同色时看不出选中
    expect(wrapper.find('.item').attributes('class')).toContain('data-[state=on]:bg-primary')
  })
})
