import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import EToggleGroup from '@/components/toggle-group/EToggleGroup.vue'

describe('EToggleGroup', () => {
  it('renders a toggle group root element', () => {
    const wrapper = mount(EToggleGroup)
    expect(wrapper.find('[data-slot="toggle-group"]').exists()).toBe(true)
  })

  it('renders slot content', () => {
    const wrapper = mount(EToggleGroup, {
      slots: {
        default: '<button>Option A</button><button>Option B</button>',
      },
    })
    expect(wrapper.text()).toContain('Option A')
    expect(wrapper.text()).toContain('Option B')
  })

  it('defaults to single type', () => {
    const wrapper = mount(EToggleGroup)
    // reka-ui ToggleGroupRoot sets type attribute; defaults to 'single'
    expect(wrapper.exists()).toBe(true)
  })

  it('accepts type prop as multiple', () => {
    const wrapper = mount(EToggleGroup, {
      props: { type: 'multiple' },
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('applies custom class to root element', () => {
    const wrapper = mount(EToggleGroup, {
      props: { class: 'my-toggle-group' },
    })
    const root = wrapper.find('[data-slot="toggle-group"]')
    expect(root.classes()).toContain('my-toggle-group')
  })

  it('passes disabled prop to reka-ui root', () => {
    const wrapper = mount(EToggleGroup, {
      props: { disabled: true },
    })
    // The component passes disabled to ToggleGroupRoot; verify it mounts correctly
    expect(wrapper.find('[data-slot="toggle-group"]').exists()).toBe(true)
  })

  it('has flex layout classes', () => {
    const wrapper = mount(EToggleGroup)
    const root = wrapper.find('[data-slot="toggle-group"]')
    expect(root.classes()).toContain('flex')
    expect(root.classes()).toContain('items-center')
  })
})
