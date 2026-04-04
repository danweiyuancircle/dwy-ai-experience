import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import ECascader from '@/components/cascader/ECascader.vue'

describe('ECascader', () => {
  it('renders a trigger button', () => {
    const wrapper = mount(ECascader, {
      props: { options: [] },
    })
    expect(wrapper.find('button').exists()).toBe(true)
  })

  it('displays placeholder when no value is selected', () => {
    const wrapper = mount(ECascader, {
      props: {
        options: [],
        placeholder: 'Pick an option',
      },
    })
    expect(wrapper.text()).toContain('Pick an option')
  })

  it('shows default placeholder text', () => {
    const wrapper = mount(ECascader, {
      props: { options: [] },
    })
    expect(wrapper.text()).toContain('Select...')
  })

  it('disables trigger when disabled prop is true', () => {
    const wrapper = mount(ECascader, {
      props: { options: [], disabled: true },
    })
    expect(wrapper.find('button').attributes('disabled')).toBeDefined()
  })

  it('accepts options prop without error', () => {
    const options = [
      { label: 'A', value: 'a', children: [{ label: 'A1', value: 'a1' }] },
      { label: 'B', value: 'b' },
    ]
    const wrapper = mount(ECascader, {
      props: { options },
    })
    expect(wrapper.find('button').exists()).toBe(true)
  })
})
