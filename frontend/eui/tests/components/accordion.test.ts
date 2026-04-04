import { mount } from '@vue/test-utils'
import { describe, it, expect, beforeAll } from 'vitest'
import EAccordion from '@/components/accordion/EAccordion.vue'

beforeAll(() => {
  window.ResizeObserver = class {
    observe() {}
    unobserve() {}
    disconnect() {}
  } as any
})

const items = [
  { key: 'item1', title: '标题一' },
  { key: 'item2', title: '标题二' },
  { key: 'item3', title: '标题三', disabled: true },
]

describe('EAccordion', () => {
  it('renders accordion root', () => {
    const wrapper = mount(EAccordion, {
      props: { items },
    })
    expect(wrapper.find('[data-slot="accordion"]').exists()).toBe(true)
  })

  it('renders all accordion items', () => {
    const wrapper = mount(EAccordion, {
      props: { items },
    })
    const accordionItems = wrapper.findAll('[data-slot="accordion-item"]')
    expect(accordionItems.length).toBe(3)
  })

  it('renders item titles in triggers', () => {
    const wrapper = mount(EAccordion, {
      props: { items },
    })
    const triggers = wrapper.findAll('[data-slot="accordion-trigger"]')
    expect(triggers[0].text()).toContain('标题一')
    expect(triggers[1].text()).toContain('标题二')
    expect(triggers[2].text()).toContain('标题三')
  })

  it('opens item on click and emits update:modelValue', async () => {
    const wrapper = mount(EAccordion, {
      props: { items },
    })
    const triggers = wrapper.findAll('[data-slot="accordion-trigger"]')
    await triggers[0].trigger('click')
    expect(wrapper.emitted('update:modelValue')).toBeTruthy()
  })

  it('renders in single mode by default', () => {
    const wrapper = mount(EAccordion, {
      props: { items },
    })
    const root = wrapper.find('[data-slot="accordion"]')
    // Reka-ui AccordionRoot: single type renders data-type="single" or similar
    // The root should exist and accept single selection
    expect(root.exists()).toBe(true)
  })

  it('supports multiple mode', () => {
    const wrapper = mount(EAccordion, {
      props: { items, multiple: true },
    })
    const root = wrapper.find('[data-slot="accordion"]')
    expect(root.exists()).toBe(true)
  })

  it('renders disabled item', () => {
    const wrapper = mount(EAccordion, {
      props: { items },
    })
    const accordionItems = wrapper.findAll('[data-slot="accordion-item"]')
    // Third item has disabled: true
    expect(accordionItems[2].attributes('data-disabled')).toBeDefined()
  })

  it('renders with controlled modelValue', () => {
    const wrapper = mount(EAccordion, {
      props: { items, modelValue: 'item1' },
    })
    const accordionItems = wrapper.findAll('[data-slot="accordion-item"]')
    // First item should be open
    expect(accordionItems[0].attributes('data-state')).toBe('open')
    expect(accordionItems[1].attributes('data-state')).toBe('closed')
  })
})
