import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import ETransfer from '@/components/transfer/ETransfer.vue'

const mockData = [
  { label: 'Option A', value: 1 },
  { label: 'Option B', value: 2 },
  { label: 'Option C', value: 3 },
  { label: 'Option D', value: 4 },
]

describe('ETransfer', () => {
  it('renders left and right panels', () => {
    const wrapper = mount(ETransfer)
    // Each panel is a direct child flex-col div with border
    const panels = wrapper.findAll('[class*="flex-col"][class*="rounded-md"][class*="border"][class*="min-w-"]')
    expect(panels.length).toBe(2)
  })

  it('renders default titles', () => {
    const wrapper = mount(ETransfer, { props: { data: mockData } })
    expect(wrapper.text()).toContain('Source')
    expect(wrapper.text()).toContain('Target')
  })

  it('renders custom titles', () => {
    const wrapper = mount(ETransfer, {
      props: { data: mockData, titles: ['Left Panel', 'Right Panel'] as [string, string] },
    })
    expect(wrapper.text()).toContain('Left Panel')
    expect(wrapper.text()).toContain('Right Panel')
  })

  it('renders data items in left panel', () => {
    const wrapper = mount(ETransfer, { props: { data: mockData } })
    expect(wrapper.text()).toContain('Option A')
    expect(wrapper.text()).toContain('Option B')
    expect(wrapper.text()).toContain('Option C')
    expect(wrapper.text()).toContain('Option D')
  })

  it('splits items between panels based on modelValue', () => {
    const wrapper = mount(ETransfer, {
      props: { data: mockData, modelValue: [1, 3] },
    })
    const panels = wrapper.findAll('[class*="flex-col"][class*="rounded-md"][class*="border"][class*="min-w-"]')
    const leftPanel = panels[0]
    const rightPanel = panels[1]

    // Left panel should have items NOT in modelValue
    expect(leftPanel.text()).toContain('Option B')
    expect(leftPanel.text()).toContain('Option D')

    // Right panel should have items IN modelValue
    expect(rightPanel.text()).toContain('Option A')
    expect(rightPanel.text()).toContain('Option C')
  })

  it('renders filter inputs when filterable is true', () => {
    const wrapper = mount(ETransfer, {
      props: { data: mockData, filterable: true },
    })
    const filterInputs = wrapper.findAll('input[type="text"]')
    expect(filterInputs.length).toBe(2)
  })

  it('does not render filter inputs when filterable is false', () => {
    const wrapper = mount(ETransfer, {
      props: { data: mockData, filterable: false },
    })
    const filterInputs = wrapper.findAll('input[type="text"]')
    expect(filterInputs.length).toBe(0)
  })

  it('renders move buttons', () => {
    const wrapper = mount(ETransfer, { props: { data: mockData } })
    const buttons = wrapper.findAll('button')
    // Should have 2 move buttons (right and left)
    expect(buttons.length).toBe(2)
  })

  it('disables move buttons when nothing is checked', () => {
    const wrapper = mount(ETransfer, { props: { data: mockData } })
    const buttons = wrapper.findAll('button')
    expect(buttons[0].attributes('disabled')).toBeDefined()
    expect(buttons[1].attributes('disabled')).toBeDefined()
  })

  it('renders checkboxes for each item', () => {
    const wrapper = mount(ETransfer, { props: { data: mockData } })
    const checkboxes = wrapper.findAll('input[type="checkbox"]')
    // 2 select-all checkboxes + 4 item checkboxes
    expect(checkboxes.length).toBe(6)
  })
})
