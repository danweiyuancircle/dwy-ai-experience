import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import ECheckbox from '@/components/checkbox/ECheckbox.vue'

describe('ECheckbox', () => {
  it('renders a single checkbox by default', () => {
    const wrapper = mount(ECheckbox)
    expect(wrapper.find('[data-slot="checkbox-wrapper"]').exists()).toBe(true)
    expect(wrapper.find('[data-slot="checkbox"]').exists()).toBe(true)
    // Should render as a button element (reka-ui CheckboxRoot)
    expect(wrapper.find('button[data-slot="checkbox"]').exists()).toBe(true)
  })

  it('passes modelValue false as unchecked state', () => {
    const wrapper = mount(ECheckbox, {
      props: { modelValue: false },
    })
    const btn = wrapper.find('[data-slot="checkbox"]')
    expect(btn.attributes('data-state')).toBe('unchecked')
  })

  it('renders label text when label prop is provided', () => {
    const wrapper = mount(ECheckbox, {
      props: { label: '同意协议' },
    })
    expect(wrapper.text()).toContain('同意协议')
  })

  it('does not render label span when no label prop and no slot', () => {
    const wrapper = mount(ECheckbox)
    const spans = wrapper.findAll('span')
    expect(spans.length).toBe(0)
  })

  it('renders slot content instead of label prop', () => {
    const wrapper = mount(ECheckbox, {
      props: { label: '会被覆盖' },
      slots: { default: '自定义内容' },
    })
    expect(wrapper.text()).toContain('自定义内容')
    expect(wrapper.text()).not.toContain('会被覆盖')
  })

  it('applies disabled state', () => {
    const wrapper = mount(ECheckbox, {
      props: { disabled: true },
    })
    const btn = wrapper.find('[data-slot="checkbox"]')
    expect(btn.attributes('disabled')).toBeDefined()
    expect(wrapper.find('[data-slot="checkbox-wrapper"]').classes()).toContain('cursor-not-allowed')
  })

  it('applies cursor-pointer when not disabled', () => {
    const wrapper = mount(ECheckbox, {
      props: { disabled: false },
    })
    expect(wrapper.find('[data-slot="checkbox-wrapper"]').classes()).toContain('cursor-pointer')
  })

  it('renders indeterminate data-state on reka-ui CheckboxRoot', () => {
    const wrapper = mount(ECheckbox, {
      props: { modelValue: false, indeterminate: true },
    })
    const btn = wrapper.find('[data-slot="checkbox"]')
    expect(btn.attributes('data-state')).toBe('indeterminate')
  })

  it('emits update:modelValue when reka-ui CheckboxRoot toggles', async () => {
    // 回归保护：reka-ui v2 改名 checked → modelValue 后桥接断裂，
    // UI 显示已勾选但外层 v-model 不更新（注册页"请先同意协议"误报的根因）
    const wrapper = mount(ECheckbox, {
      props: { modelValue: false },
    })
    await wrapper.find('[data-slot="checkbox"]').trigger('click')
    expect(wrapper.emitted('update:modelValue')).toBeTruthy()
    expect(wrapper.emitted('update:modelValue')![0]).toEqual([true])
  })

  it('renders group mode when options are provided', () => {
    const options = [
      { label: '苹果', value: 'apple' },
      { label: '香蕉', value: 'banana' },
      { label: '橙子', value: 'orange' },
    ]
    const wrapper = mount(ECheckbox, {
      props: { options, modelValue: [] },
    })
    expect(wrapper.find('[data-slot="checkbox-group"]').exists()).toBe(true)
    const items = wrapper.findAll('[data-slot="checkbox"]')
    expect(items.length).toBe(3)
    expect(wrapper.text()).toContain('苹果')
    expect(wrapper.text()).toContain('香蕉')
    expect(wrapper.text()).toContain('橙子')
  })

  it('does not render group when options is empty', () => {
    const wrapper = mount(ECheckbox, {
      props: { options: [], modelValue: false },
    })
    expect(wrapper.find('[data-slot="checkbox-group"]').exists()).toBe(false)
    expect(wrapper.find('[data-slot="checkbox-wrapper"]').exists()).toBe(true)
  })

  it('disables individual option in group mode', () => {
    const options = [
      { label: '苹果', value: 'apple' },
      { label: '香蕉', value: 'banana', disabled: true },
    ]
    const wrapper = mount(ECheckbox, {
      props: { options, modelValue: [] },
    })
    const checkboxes = wrapper.findAll('[data-slot="checkbox"]')
    expect(checkboxes[0].attributes('disabled')).toBeUndefined()
    expect(checkboxes[1].attributes('disabled')).toBeDefined()
  })

  it('applies vertical direction in group mode', () => {
    const options = [
      { label: 'A', value: 'a' },
      { label: 'B', value: 'b' },
    ]
    const wrapper = mount(ECheckbox, {
      props: { options, modelValue: [], direction: 'vertical' },
    })
    const group = wrapper.find('[data-slot="checkbox-group"]')
    expect(group.classes()).toContain('grid')
  })

  it('applies horizontal direction in group mode by default', () => {
    const options = [
      { label: 'A', value: 'a' },
      { label: 'B', value: 'b' },
    ]
    const wrapper = mount(ECheckbox, {
      props: { options, modelValue: [] },
    })
    const group = wrapper.find('[data-slot="checkbox-group"]')
    expect(group.classes()).toContain('flex-row')
  })
})
