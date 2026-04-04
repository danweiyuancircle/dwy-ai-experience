import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import EButtonGroup from '@/components/button-group/EButtonGroup.vue'

describe('EButtonGroup', () => {
  it('renders a button group element with role="group"', () => {
    const wrapper = mount(EButtonGroup)
    const root = wrapper.find('[data-slot="button-group"]')
    expect(root.exists()).toBe(true)
    expect(root.attributes('role')).toBe('group')
  })

  it('renders slot content', () => {
    const wrapper = mount(EButtonGroup, {
      slots: {
        default: '<button>Btn 1</button><button>Btn 2</button><button>Btn 3</button>',
      },
    })
    expect(wrapper.text()).toContain('Btn 1')
    expect(wrapper.text()).toContain('Btn 2')
    expect(wrapper.text()).toContain('Btn 3')
  })

  it('applies horizontal orientation by default', () => {
    const wrapper = mount(EButtonGroup)
    const root = wrapper.find('[data-slot="button-group"]')
    expect(root.attributes('data-orientation')).toBe('horizontal')
  })

  it('applies vertical orientation when specified', () => {
    const wrapper = mount(EButtonGroup, {
      props: { orientation: 'vertical' },
    })
    const root = wrapper.find('[data-slot="button-group"]')
    expect(root.attributes('data-orientation')).toBe('vertical')
    expect(root.classes()).toContain('flex-col')
  })

  it('does not have flex-col class for horizontal orientation', () => {
    const wrapper = mount(EButtonGroup, {
      props: { orientation: 'horizontal' },
    })
    const root = wrapper.find('[data-slot="button-group"]')
    expect(root.classes()).not.toContain('flex-col')
  })

  it('applies custom class to root element', () => {
    const wrapper = mount(EButtonGroup, {
      props: { class: 'my-btn-group' },
    })
    const root = wrapper.find('[data-slot="button-group"]')
    expect(root.classes()).toContain('my-btn-group')
  })

  it('has flex layout classes', () => {
    const wrapper = mount(EButtonGroup)
    const root = wrapper.find('[data-slot="button-group"]')
    expect(root.classes()).toContain('flex')
  })
})
