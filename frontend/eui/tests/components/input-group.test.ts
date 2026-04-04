import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import EInputGroup from '@/components/input-group/EInputGroup.vue'
import EInputGroupAddon from '@/components/input-group/EInputGroupAddon.vue'

describe('EInputGroup', () => {
  it('renders a group container with role="group"', () => {
    const wrapper = mount(EInputGroup)
    expect(wrapper.attributes('role')).toBe('group')
  })

  it('has data-slot="input-group" attribute', () => {
    const wrapper = mount(EInputGroup)
    expect(wrapper.attributes('data-slot')).toBe('input-group')
  })

  it('renders default slot content', () => {
    const wrapper = mount(EInputGroup, {
      slots: {
        default: '<input type="text" placeholder="test" />',
      },
    })
    const input = wrapper.find('input')
    expect(input.exists()).toBe(true)
    expect(input.attributes('placeholder')).toBe('test')
  })

  it('renders multiple children in slot', () => {
    const wrapper = mount(EInputGroup, {
      slots: {
        default: '<span>prefix</span><input type="text" /><span>suffix</span>',
      },
    })
    const spans = wrapper.findAll('span')
    expect(spans).toHaveLength(2)
    expect(wrapper.find('input').exists()).toBe(true)
  })

  it('applies custom class', () => {
    const wrapper = mount(EInputGroup, {
      props: { class: 'my-group-class' },
    })
    expect(wrapper.classes()).toContain('my-group-class')
  })
})

describe('EInputGroupAddon', () => {
  it('renders with data-slot="input-group-addon"', () => {
    const wrapper = mount(EInputGroupAddon)
    expect(wrapper.attributes('data-slot')).toBe('input-group-addon')
  })

  it('renders slot content', () => {
    const wrapper = mount(EInputGroupAddon, {
      slots: {
        default: '<span>@</span>',
      },
    })
    expect(wrapper.find('span').text()).toBe('@')
  })

  it('defaults to inline-start align', () => {
    const wrapper = mount(EInputGroupAddon)
    expect(wrapper.attributes('data-align')).toBe('inline-start')
  })

  it('applies inline-end align', () => {
    const wrapper = mount(EInputGroupAddon, {
      props: { align: 'inline-end' },
    })
    expect(wrapper.attributes('data-align')).toBe('inline-end')
    expect(wrapper.classes().join(' ')).toContain('order-last')
  })

  it('applies custom class', () => {
    const wrapper = mount(EInputGroupAddon, {
      props: { class: 'addon-custom' },
    })
    expect(wrapper.classes()).toContain('addon-custom')
  })
})

describe('EInputGroup + EInputGroupAddon composition', () => {
  it('renders addon inside input group', () => {
    const wrapper = mount(EInputGroup, {
      slots: {
        default: {
          template: '<EInputGroupAddon><span>$</span></EInputGroupAddon><input type="text" />',
          components: { EInputGroupAddon },
        },
      },
    })
    expect(wrapper.find('[data-slot="input-group-addon"]').exists()).toBe(true)
    expect(wrapper.find('input').exists()).toBe(true)
    expect(wrapper.find('span').text()).toBe('$')
  })
})
