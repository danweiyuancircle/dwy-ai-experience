import { mount } from '@vue/test-utils'
import { describe, it, expect, beforeAll } from 'vitest'
import ECalendar from '@/components/calendar/ECalendar.vue'

beforeAll(() => {
  window.ResizeObserver = class {
    observe() {}
    unobserve() {}
    disconnect() {}
  } as any
})

describe('ECalendar', () => {
  it('renders calendar root', () => {
    const wrapper = mount(ECalendar)
    expect(wrapper.find('[data-slot="calendar"]').exists()).toBe(true)
  })

  it('renders navigation buttons', () => {
    const wrapper = mount(ECalendar)
    const buttons = wrapper.findAll('button')
    // Should have prev and next navigation buttons
    expect(buttons.length).toBeGreaterThanOrEqual(2)
  })

  it('renders calendar grid with day cells', () => {
    const wrapper = mount(ECalendar)
    // Calendar should render day cells (buttons inside the grid)
    const cells = wrapper.findAll('td')
    expect(cells.length).toBeGreaterThan(0)
  })

  it('renders weekday headers', () => {
    const wrapper = mount(ECalendar)
    // Should have weekday header cells
    const headCells = wrapper.findAll('th')
    expect(headCells.length).toBe(7)
  })

  it('applies custom class', () => {
    const wrapper = mount(ECalendar, {
      props: { class: 'my-calendar' },
    })
    const root = wrapper.find('[data-slot="calendar"]')
    expect(root.classes()).toContain('my-calendar')
  })
})
