import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import EContextMenu from '@/components/context-menu/EContextMenu.vue'

describe('EContextMenu', () => {
  it('renders without error', () => {
    const wrapper = mount(EContextMenu, {
      slots: { default: '<div>Right click here</div>' },
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('renders the trigger slot content', () => {
    const wrapper = mount(EContextMenu, {
      slots: { default: '<div>Context area</div>' },
    })
    expect(wrapper.find('[data-slot="context-menu-trigger"]').exists()).toBe(true)
    expect(wrapper.text()).toContain('Context area')
  })

  it('does not render menu content in closed state (portal)', () => {
    const wrapper = mount(EContextMenu, {
      props: {
        items: [
          { key: 'copy', label: 'Copy' },
          { key: 'paste', label: 'Paste' },
        ],
      },
      slots: { default: '<div>Right click</div>' },
    })
    // Menu content is portaled and only appears on right-click
    expect(wrapper.find('[data-slot="context-menu-content"]').exists()).toBe(false)
  })

  it('accepts items prop without error', () => {
    const wrapper = mount(EContextMenu, {
      props: {
        items: [
          { key: 'edit', label: 'Edit' },
          { key: 'delete', label: 'Delete', variant: 'destructive' as const },
        ],
      },
      slots: { default: '<div>Right click</div>' },
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('accepts empty items array', () => {
    const wrapper = mount(EContextMenu, {
      props: { items: [] },
      slots: { default: '<div>Right click</div>' },
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('accepts items with children (sub-menu)', () => {
    const wrapper = mount(EContextMenu, {
      props: {
        items: [
          {
            key: 'more',
            label: 'More',
            children: [
              { key: 'sub1', label: 'Sub Item 1' },
              { key: 'sub2', label: 'Sub Item 2' },
            ],
          },
        ],
      },
      slots: { default: '<div>Right click</div>' },
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('accepts items with disabled and divided flags', () => {
    const wrapper = mount(EContextMenu, {
      props: {
        items: [
          { key: 'copy', label: 'Copy' },
          { key: 'delete', label: 'Delete', disabled: true, divided: true },
        ],
      },
      slots: { default: '<div>Right click</div>' },
    })
    expect(wrapper.exists()).toBe(true)
  })
})
