import { mount, flushPromises } from '@vue/test-utils'
import { nextTick } from 'vue'
import { describe, it, expect } from 'vitest'
import ETree from '@/components/tree/ETree.vue'

const treeData = [
  {
    key: '1',
    label: '节点一',
    children: [
      { key: '1-1', label: '子节点 1-1' },
      { key: '1-2', label: '子节点 1-2' },
    ],
  },
  {
    key: '2',
    label: '节点二',
    children: [
      { key: '2-1', label: '子节点 2-1' },
    ],
  },
  {
    key: '3',
    label: '节点三',
  },
]

describe('ETree', () => {
  it('renders tree root element', () => {
    const wrapper = mount(ETree, {
      props: { data: treeData },
    })
    expect(wrapper.find('[data-slot="tree"]').exists()).toBe(true)
    expect(wrapper.find('ul[role="tree"]').exists()).toBe(true)
  })

  it('renders top-level nodes', () => {
    const wrapper = mount(ETree, {
      props: { data: treeData },
    })
    expect(wrapper.text()).toContain('节点一')
    expect(wrapper.text()).toContain('节点二')
    expect(wrapper.text()).toContain('节点三')
  })

  it('does not show children by default (collapsed)', () => {
    const wrapper = mount(ETree, {
      props: { data: treeData },
    })
    expect(wrapper.text()).not.toContain('子节点 1-1')
    expect(wrapper.text()).not.toContain('子节点 2-1')
  })

  it('shows all children when defaultExpandAll is true', async () => {
    const wrapper = mount(ETree, {
      props: { data: treeData, defaultExpandAll: true },
    })
    await flushPromises()
    await nextTick()
    expect(wrapper.text()).toContain('子节点 1-1')
    expect(wrapper.text()).toContain('子节点 1-2')
    expect(wrapper.text()).toContain('子节点 2-1')
  })

  it('renders checkboxes when checkable is true', () => {
    const wrapper = mount(ETree, {
      props: { data: treeData, checkable: true, modelValue: [] },
    })
    const checkboxes = wrapper.findAll('input[type="checkbox"]')
    // Only top-level nodes visible (3 nodes), each has a checkbox
    expect(checkboxes.length).toBe(3)
  })

  it('renders checkboxes for expanded children', async () => {
    const wrapper = mount(ETree, {
      props: { data: treeData, checkable: true, modelValue: [], defaultExpandAll: true },
    })
    await flushPromises()
    await nextTick()
    const checkboxes = wrapper.findAll('input[type="checkbox"]')
    // All 6 nodes visible (3 top + 2 under node1 + 1 under node2)
    expect(checkboxes.length).toBe(6)
  })

  it('checks nodes matching modelValue', () => {
    const wrapper = mount(ETree, {
      props: { data: treeData, checkable: true, modelValue: ['1', '3'] },
    })
    const checkboxes = wrapper.findAll('input[type="checkbox"]')
    const checkedStates = checkboxes.map((cb) => (cb.element as HTMLInputElement).checked)
    // Node 1 checked, Node 2 unchecked, Node 3 checked
    expect(checkedStates).toEqual([true, false, true])
  })

  it('shows expanded children when expandedKeys is provided', async () => {
    const wrapper = mount(ETree, {
      props: { data: treeData, expandedKeys: ['1'] },
    })
    await flushPromises()
    await nextTick()
    expect(wrapper.text()).toContain('子节点 1-1')
    expect(wrapper.text()).toContain('子节点 1-2')
    expect(wrapper.text()).not.toContain('子节点 2-1')
  })
})
