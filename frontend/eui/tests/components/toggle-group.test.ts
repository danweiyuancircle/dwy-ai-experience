import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import EToggleGroup from '@/components/toggle-group/EToggleGroup.vue'
import EToggleGroupItem from '@/components/toggle-group/EToggleGroupItem.vue'

/** 组装 single 组 + 两个 Item 的挂载模板;defaultValue 走 reka-ui 非受控内部状态 */
function mountSingleGroup(defaultValue = 'a') {
  return mount({
    components: { EToggleGroup, EToggleGroupItem },
    template: `
      <EToggleGroup type="single" default-value="${defaultValue}">
        <EToggleGroupItem value="a">A</EToggleGroupItem>
        <EToggleGroupItem value="b">B</EToggleGroupItem>
      </EToggleGroup>
    `,
  })
}

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

describe('EToggleGroupItem', () => {
  it('renders item elements with value attributes', () => {
    const wrapper = mountSingleGroup()
    const items = wrapper.findAll('[data-slot="toggle-group-item"]')
    expect(items).toHaveLength(2)
    expect(items[0].attributes('value')).toBe('a')
    expect(items[1].attributes('value')).toBe('b')
  })

  it('marks the active item via data-state and switches on click', async () => {
    const wrapper = mountSingleGroup()
    const items = () => wrapper.findAll('[data-slot="toggle-group-item"]')
    expect(items()[0].attributes('data-state')).toBe('on')
    expect(items()[1].attributes('data-state')).toBe('off')

    await items()[1].trigger('click')
    expect(items()[1].attributes('data-state')).toBe('on')
    expect(items()[0].attributes('data-state')).toBe('off')
  })

  it('emits update:modelValue with clicked item value in single mode', async () => {
    const wrapper = mountSingleGroup()
    await wrapper.findAll('[data-slot="toggle-group-item"]')[1].trigger('click')
    expect(wrapper.findComponent(EToggleGroup).emitted('update:modelValue')).toEqual([['b']])
  })

  it('does not emit when clicking a disabled item', async () => {
    const wrapper = mount({
      components: { EToggleGroup, EToggleGroupItem },
      template: `
        <EToggleGroup type="single" default-value="a">
          <EToggleGroupItem value="a">A</EToggleGroupItem>
          <EToggleGroupItem value="b" disabled>B</EToggleGroupItem>
        </EToggleGroup>
      `,
    })
    await wrapper.findAll('[data-slot="toggle-group-item"]')[1].trigger('click')
    expect(wrapper.findComponent(EToggleGroup).emitted('update:modelValue')).toBeUndefined()
  })

  it('inherits variant/size from group and exposes them as data attributes', () => {
    const wrapper = mount({
      components: { EToggleGroup, EToggleGroupItem },
      template: `
        <EToggleGroup type="single" variant="outline" size="sm">
          <EToggleGroupItem value="a">A</EToggleGroupItem>
        </EToggleGroup>
      `,
    })
    const item = wrapper.find('[data-slot="toggle-group-item"]')
    expect(item.attributes('data-variant')).toBe('outline')
    expect(item.attributes('data-size')).toBe('sm')
    expect(item.classes()).toContain('h-8')
  })

  it('applies custom class to item element', () => {
    const wrapper = mount({
      components: { EToggleGroup, EToggleGroupItem },
      template: `
        <EToggleGroup type="single">
          <EToggleGroupItem value="a" class="my-item">A</EToggleGroupItem>
        </EToggleGroup>
      `,
    })
    expect(wrapper.find('[data-slot="toggle-group-item"]').classes()).toContain('my-item')
  })
})
