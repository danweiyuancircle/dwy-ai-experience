/**
 * MetricGrid：断点看内容区，不看视口。
 */
import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import { MetricGrid } from '../../../src/components'

describe('MetricGrid', () => {
  it('默认三列，容器包在栅格外面', () => {
    const wrapper = mount(MetricGrid, { slots: { default: '<div class="card" />' } })
    const grid = wrapper.get('[data-card-grid]')

    expect(wrapper.html()).toContain('@container')
    expect(grid.classes()).toContain('grid-cols-1')
    expect(grid.classes()).toContain('@min-[36rem]:grid-cols-2')
    expect(grid.classes()).toContain('@min-[56rem]:grid-cols-3')
    expect(grid.classes().join(' ')).not.toContain('grid-cols-5')
  })

  it('两列停在两列，五列再到 72rem', () => {
    const two = mount(MetricGrid, { props: { columns: 2 } })
    const five = mount(MetricGrid, { props: { columns: 5 } })

    expect(two.get('[data-card-grid]').classes()).toContain('@min-[36rem]:grid-cols-2')
    expect(two.get('[data-card-grid]').classes().join(' ')).not.toContain('@min-[56rem]:grid-cols-3')
    expect(five.get('[data-card-grid]').classes()).toContain('@min-[72rem]:grid-cols-5')
  })
})
