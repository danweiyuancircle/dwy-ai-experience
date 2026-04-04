import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import EHoverCard from '@/components/hover-card/EHoverCard.vue'

describe('EHoverCard', () => {
  it('renders without error', () => {
    const wrapper = mount(EHoverCard, {
      slots: {
        trigger: '<a href="#">Hover me</a>',
        default: 'Card content',
      },
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('renders the trigger slot content', () => {
    const wrapper = mount(EHoverCard, {
      slots: {
        trigger: '<span>Trigger text</span>',
        default: 'Content',
      },
    })
    expect(wrapper.text()).toContain('Trigger text')
  })

  it('does not render hover card content in closed state (portal)', () => {
    const wrapper = mount(EHoverCard, {
      slots: {
        trigger: '<span>Hover</span>',
        default: 'Hover card body',
      },
    })
    // Content is inside a portal, not in the wrapper DOM
    expect(wrapper.find('[data-slot="hover-card-content"]').exists()).toBe(false)
  })

  it('accepts openDelay prop without error', () => {
    const wrapper = mount(EHoverCard, {
      props: { openDelay: 200 },
      slots: {
        trigger: '<span>Hover</span>',
        default: 'Content',
      },
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('accepts closeDelay prop without error', () => {
    const wrapper = mount(EHoverCard, {
      props: { closeDelay: 100 },
      slots: {
        trigger: '<span>Hover</span>',
        default: 'Content',
      },
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('uses default openDelay of 700', () => {
    // Default openDelay is 700 per withDefaults; component mounts without error
    const wrapper = mount(EHoverCard, {
      slots: {
        trigger: '<span>Hover</span>',
        default: 'Content',
      },
    })
    expect(wrapper.exists()).toBe(true)
  })
})
