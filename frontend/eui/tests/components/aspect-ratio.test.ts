import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import EAspectRatio from '@/components/aspect-ratio/EAspectRatio.vue'

describe('EAspectRatio', () => {
  it('renders with data-slot attribute', () => {
    const wrapper = mount(EAspectRatio)
    expect(wrapper.find('[data-slot="aspect-ratio"]').exists()).toBe(true)
  })

  it('renders slot content', () => {
    const wrapper = mount(EAspectRatio, {
      slots: { default: '<img src="test.jpg" alt="test" />' },
    })
    expect(wrapper.find('img').exists()).toBe(true)
    expect(wrapper.find('img').attributes('src')).toBe('test.jpg')
  })

  it('accepts ratio prop', () => {
    const wrapper = mount(EAspectRatio, {
      props: { ratio: 4 / 3 },
    })
    expect(wrapper.find('[data-slot="aspect-ratio"]').exists()).toBe(true)
    expect(wrapper.exists()).toBe(true)
  })

  it('accepts ratio of 1 (square)', () => {
    const wrapper = mount(EAspectRatio, {
      props: { ratio: 1 },
      slots: { default: '<div class="square-content">Square</div>' },
    })
    expect(wrapper.find('.square-content').text()).toBe('Square')
  })

  it('merges custom class on inner element', () => {
    const wrapper = mount(EAspectRatio, {
      props: { class: 'custom-ratio' },
    })
    expect(wrapper.find('.custom-ratio').exists()).toBe(true)
  })
})
