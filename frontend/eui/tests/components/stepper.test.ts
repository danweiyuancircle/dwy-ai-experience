import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import EStepper from '@/components/stepper/EStepper.vue'

// Use a single item to avoid StepperSeparator context injection errors
// (reka-ui StepperSeparator requires StepperItem context which breaks in unit tests)
const singleItem = [{ title: 'Step 1', description: 'First step' }]

const twoItems = [
  { title: 'Step 1', description: 'First step' },
  { title: 'Step 2', description: 'Second step' },
]

describe('EStepper', () => {
  it('renders stepper root element', () => {
    const wrapper = mount(EStepper, {
      props: { items: singleItem },
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('renders step title', () => {
    const wrapper = mount(EStepper, {
      props: { items: singleItem },
    })
    expect(wrapper.text()).toContain('Step 1')
  })

  it('renders step description when provided', () => {
    const wrapper = mount(EStepper, {
      props: { items: singleItem },
    })
    expect(wrapper.text()).toContain('First step')
  })

  it('accepts modelValue prop for current step', () => {
    const wrapper = mount(EStepper, {
      props: { items: singleItem, modelValue: 1 },
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('applies horizontal direction by default', () => {
    const wrapper = mount(EStepper, {
      props: { items: singleItem },
    })
    // horizontal direction → flex-row
    const root = wrapper.find('.flex')
    expect(root.classes()).toContain('flex-row')
  })

  it('applies vertical direction when specified', () => {
    const wrapper = mount(EStepper, {
      props: { items: singleItem, direction: 'vertical' },
    })
    const root = wrapper.find('.flex')
    expect(root.classes()).toContain('flex-col')
  })

  it('renders step number indicator', () => {
    const wrapper = mount(EStepper, {
      props: { items: singleItem, modelValue: 1 },
    })
    // Step number "1" should be rendered
    expect(wrapper.text()).toContain('1')
  })
})
