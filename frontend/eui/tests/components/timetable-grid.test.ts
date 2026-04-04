import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import ETimetableGrid from '@/components/timetable-grid/ETimetableGrid.vue'

describe('ETimetableGrid', () => {
  it('renders with default props', () => {
    const wrapper = mount(ETimetableGrid)
    expect(wrapper.find('[data-slot="timetable-grid"]').exists()).toBe(true)
  })

  it('renders default day headers', () => {
    const wrapper = mount(ETimetableGrid)
    expect(wrapper.text()).toContain('周一')
    expect(wrapper.text()).toContain('周五')
    expect(wrapper.text()).toContain('周日')
  })

  it('renders custom days', () => {
    const wrapper = mount(ETimetableGrid, {
      props: { days: ['Mon', 'Tue', 'Wed'] },
    })
    expect(wrapper.text()).toContain('Mon')
    expect(wrapper.text()).toContain('Tue')
    expect(wrapper.text()).toContain('Wed')
    expect(wrapper.text()).not.toContain('周一')
  })

  it('renders timetable items with data prop', () => {
    const data = [
      { day: 0, startHour: 8, endHour: 10, title: '数学课' },
      { day: 1, startHour: 10, endHour: 12, title: '英语课' },
    ]
    const wrapper = mount(ETimetableGrid, {
      props: { data },
    })
    expect(wrapper.text()).toContain('数学课')
    expect(wrapper.text()).toContain('英语课')
    expect(wrapper.text()).toContain('08:00 - 10:00')
    expect(wrapper.text()).toContain('10:00 - 12:00')
  })

  it('renders time labels based on startHour and endHour', () => {
    const wrapper = mount(ETimetableGrid, {
      props: { startHour: 9, endHour: 12 },
    })
    expect(wrapper.text()).toContain('09:00')
    expect(wrapper.text()).toContain('10:00')
    expect(wrapper.text()).toContain('11:00')
  })

  it('renders no items when data is empty', () => {
    const wrapper = mount(ETimetableGrid, {
      props: { data: [] },
    })
    expect(wrapper.find('[data-slot="timetable-grid"]').exists()).toBe(true)
    // Day headers should still render
    expect(wrapper.text()).toContain('周一')
  })
})
