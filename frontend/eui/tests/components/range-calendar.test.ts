import { mount } from '@vue/test-utils'
import { describe, it, expect, beforeAll } from 'vitest'
import ERangeCalendar from '@/components/range-calendar/ERangeCalendar.vue'

beforeAll(() => {
  window.ResizeObserver = class {
    observe() {}
    unobserve() {}
    disconnect() {}
  } as any
})

describe('ERangeCalendar', () => {
  it('renders range calendar root', () => {
    const wrapper = mount(ERangeCalendar)
    expect(wrapper.find('[data-slot="range-calendar"]').exists()).toBe(true)
  })

  it('renders navigation buttons', () => {
    const wrapper = mount(ERangeCalendar)
    const buttons = wrapper.findAll('button')
    expect(buttons.length).toBeGreaterThanOrEqual(2)
  })

  it('renders calendar grid with day cells', () => {
    const wrapper = mount(ERangeCalendar)
    const cells = wrapper.findAll('td')
    expect(cells.length).toBeGreaterThan(0)
  })

  it('renders weekday headers', () => {
    const wrapper = mount(ERangeCalendar)
    const headCells = wrapper.findAll('th')
    expect(headCells.length).toBe(7)
  })

  it('applies custom class', () => {
    const wrapper = mount(ERangeCalendar, {
      props: { class: 'my-range-cal' },
    })
    const root = wrapper.find('[data-slot="range-calendar"]')
    expect(root.classes()).toContain('my-range-cal')
  })
})
