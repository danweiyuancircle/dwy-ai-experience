import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import EAffix from '@/components/affix/EAffix.vue'

describe('EAffix', () => {
  it('renders with default props', () => {
    const wrapper = mount(EAffix, {
      slots: { default: '<div class="affix-child">Sticky</div>' },
    })
    expect(wrapper.find('.affix-child').exists()).toBe(true)
    expect(wrapper.text()).toContain('Sticky')
  })

  it('renders slot content', () => {
    const wrapper = mount(EAffix, {
      slots: { default: '<button>Back to top</button>' },
    })
    expect(wrapper.find('button').exists()).toBe(true)
    expect(wrapper.text()).toContain('Back to top')
  })

  it('accepts offset prop', () => {
    const wrapper = mount(EAffix, {
      props: { offset: 50 },
      slots: { default: '<div>content</div>' },
    })
    // Component should mount without error with offset prop
    expect(wrapper.exists()).toBe(true)
  })

  it('accepts position prop', () => {
    const wrapper = mount(EAffix, {
      props: { position: 'bottom' },
      slots: { default: '<div>content</div>' },
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('applies custom class', () => {
    const wrapper = mount(EAffix, {
      props: { class: 'my-affix' },
      slots: { default: '<div>content</div>' },
    })
    expect(wrapper.html()).toContain('my-affix')
  })

  it('is not fixed by default (not scrolled)', () => {
    const wrapper = mount(EAffix, {
      slots: { default: '<div>content</div>' },
    })
    // By default, placeholder should not have a height style (not fixed)
    const outerDiv = wrapper.element as HTMLElement
    expect(outerDiv.style.height).toBeFalsy()
  })
})
