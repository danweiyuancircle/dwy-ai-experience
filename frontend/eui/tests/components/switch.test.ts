import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import ESwitch from '@/components/switch/ESwitch.vue'

describe('ESwitch', () => {
  it('renders a switch element by default', () => {
    const wrapper = mount(ESwitch)
    expect(wrapper.find('[data-slot="switch-wrapper"]').exists()).toBe(true)
    expect(wrapper.find('[data-slot="switch"]').exists()).toBe(true)
    expect(wrapper.find('[data-slot="switch-thumb"]').exists()).toBe(true)
  })

  it('renders unchecked state when modelValue is false', () => {
    const wrapper = mount(ESwitch, {
      props: { modelValue: false },
    })
    const switchRoot = wrapper.find('[data-slot="switch"]')
    expect(switchRoot.attributes('data-state')).toBe('unchecked')
  })

  it('renders label text when label prop is provided', () => {
    const wrapper = mount(ESwitch, {
      props: { label: '启用通知' },
    })
    expect(wrapper.text()).toContain('启用通知')
  })

  it('does not render label span when no label prop and no slot', () => {
    const wrapper = mount(ESwitch)
    const spans = wrapper.findAll('span.text-sm')
    expect(spans.length).toBe(0)
  })

  it('renders slot content instead of label prop', () => {
    const wrapper = mount(ESwitch, {
      props: { label: '会被覆盖' },
      slots: { default: '自定义标签' },
    })
    expect(wrapper.text()).toContain('自定义标签')
    expect(wrapper.text()).not.toContain('会被覆盖')
  })

  it('applies sm size class', () => {
    const wrapper = mount(ESwitch, {
      props: { size: 'sm' },
    })
    const switchRoot = wrapper.find('[data-slot="switch"]')
    expect(switchRoot.classes()).toContain('w-6')
    const thumb = wrapper.find('[data-slot="switch-thumb"]')
    expect(thumb.classes()).toContain('size-3')
  })

  it('applies lg size class', () => {
    const wrapper = mount(ESwitch, {
      props: { size: 'lg' },
    })
    const switchRoot = wrapper.find('[data-slot="switch"]')
    expect(switchRoot.classes()).toContain('w-10')
    const thumb = wrapper.find('[data-slot="switch-thumb"]')
    expect(thumb.classes()).toContain('size-5')
  })

  it('applies default size class when no size prop', () => {
    const wrapper = mount(ESwitch)
    const switchRoot = wrapper.find('[data-slot="switch"]')
    expect(switchRoot.classes()).toContain('w-8')
    const thumb = wrapper.find('[data-slot="switch-thumb"]')
    expect(thumb.classes()).toContain('size-4')
  })

  it('applies disabled state', () => {
    const wrapper = mount(ESwitch, {
      props: { disabled: true },
    })
    const switchRoot = wrapper.find('[data-slot="switch"]')
    expect(switchRoot.attributes('disabled')).toBeDefined()
    expect(wrapper.find('[data-slot="switch-wrapper"]').classes()).toContain('cursor-not-allowed')
  })

  it('applies cursor-pointer when not disabled', () => {
    const wrapper = mount(ESwitch, {
      props: { disabled: false },
    })
    expect(wrapper.find('[data-slot="switch-wrapper"]').classes()).toContain('cursor-pointer')
  })
})
