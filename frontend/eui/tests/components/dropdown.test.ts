import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import EDropdown from '@/components/dropdown/EDropdown.vue'

const baseItems = [
  { key: 'edit', label: 'Edit' },
  { key: 'delete', label: 'Delete', variant: 'destructive' as const },
  { key: 'copy', label: 'Copy', disabled: true },
]

describe('EDropdown', () => {
  it('renders a dropdown root element', () => {
    const wrapper = mount(EDropdown, {
      slots: { default: '<button>Open</button>' },
    })
    expect(wrapper.text()).toContain('Open')
  })

  it('renders trigger slot content', () => {
    const wrapper = mount(EDropdown, {
      slots: { default: '<button class="my-trigger">Menu</button>' },
    })
    expect(wrapper.find('.my-trigger').exists()).toBe(true)
  })

  it('accepts items prop without error', () => {
    const wrapper = mount(EDropdown, {
      props: { items: baseItems },
      slots: { default: '<button>Open</button>' },
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('renders split button mode when splitButton is true', () => {
    const wrapper = mount(EDropdown, {
      props: {
        splitButton: true,
        buttonText: 'Action',
        items: baseItems,
      },
    })
    expect(wrapper.find('[data-slot="dropdown-split-button"]').exists()).toBe(true)
    expect(wrapper.text()).toContain('Action')
  })

  it('emits click event on split button primary click', async () => {
    const wrapper = mount(EDropdown, {
      props: {
        splitButton: true,
        buttonText: 'Action',
        items: baseItems,
      },
    })
    const primaryBtn = wrapper.find('[data-slot="dropdown-split-primary"]')
    await primaryBtn.trigger('click')
    expect(wrapper.emitted('click')).toBeTruthy()
  })

  it('applies side and align props', () => {
    const wrapper = mount(EDropdown, {
      props: {
        items: baseItems,
        side: 'right',
        align: 'end',
      },
      slots: { default: '<button>Open</button>' },
    })
    // Component should mount without errors with these props
    expect(wrapper.exists()).toBe(true)
  })
})
