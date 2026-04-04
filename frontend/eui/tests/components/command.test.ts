import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import ECommand from '@/components/command/ECommand.vue'

describe('ECommand', () => {
  it('renders with default props', () => {
    const wrapper = mount(ECommand, {
      slots: { default: '<div>command items</div>' },
    })
    expect(wrapper.find('[data-slot="command"]').exists()).toBe(true)
  })

  it('renders slot content', () => {
    const wrapper = mount(ECommand, {
      slots: { default: '<span class="test-item">Search...</span>' },
    })
    expect(wrapper.find('.test-item').exists()).toBe(true)
    expect(wrapper.text()).toContain('Search...')
  })

  it('applies custom class', () => {
    const wrapper = mount(ECommand, {
      props: { class: 'my-command' },
      slots: { default: '<div>items</div>' },
    })
    const el = wrapper.find('[data-slot="command"]')
    expect(el.classes()).toContain('my-command')
  })

  it('has data-slot attribute', () => {
    const wrapper = mount(ECommand, {
      slots: { default: '<div>items</div>' },
    })
    expect(wrapper.find('[data-slot="command"]').attributes('data-slot')).toBe('command')
  })
})
