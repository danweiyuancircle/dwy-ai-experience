import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import ETreeSelect from '@/components/tree-select/ETreeSelect.vue'

describe('ETreeSelect', () => {
  it('renders a trigger button', () => {
    const wrapper = mount(ETreeSelect)
    expect(wrapper.find('button').exists()).toBe(true)
  })

  it('displays placeholder when no value is selected', () => {
    const wrapper = mount(ETreeSelect, {
      props: { placeholder: 'Choose item' },
    })
    expect(wrapper.text()).toContain('Choose item')
  })

  it('shows default placeholder text', () => {
    const wrapper = mount(ETreeSelect)
    expect(wrapper.text()).toContain('Select...')
  })

  it('accepts data prop without error', () => {
    const data = [
      { key: '1', label: 'Node 1', children: [{ key: '1-1', label: 'Child 1' }] },
      { key: '2', label: 'Node 2' },
    ]
    const wrapper = mount(ETreeSelect, {
      props: { data },
    })
    expect(wrapper.find('button').exists()).toBe(true)
  })

  it('disables trigger when disabled prop is true', () => {
    const wrapper = mount(ETreeSelect, {
      props: { disabled: true },
    })
    expect(wrapper.find('button').attributes('disabled')).toBeDefined()
  })
})
