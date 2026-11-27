import { mount } from '@vue/test-utils'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { EBarChart, EDonutChart, ELineChart } from '../../src/charts'

// 绘图由 Chrome 验证。jsdom 没有 Unovis 使用的 SVG 文本测量 API。
const stub = vi.hoisted(() => (name: string) => ({ default: { name, template: '<div><slot /></div>' } }))
vi.mock('@unovis/vue/containers/xy-container', () => stub('VisXYContainer'))
vi.mock('@unovis/vue/containers/single-container', () => stub('VisSingleContainer'))
vi.mock('@unovis/vue/components/grouped-bar', () => stub('VisGroupedBar'))
vi.mock('@unovis/vue/components/line', () => stub('VisLine'))
vi.mock('@unovis/vue/components/donut', () => ({ ...stub('VisDonut'), VisDonutSelectors: { segment: 'segment' } }))
vi.mock('@unovis/vue/components/axis', () => stub('VisAxis'))
vi.mock('@unovis/vue/components/crosshair', () => stub('VisCrosshair'))
vi.mock('@unovis/vue/components/tooltip', () => stub('VisTooltip'))

const wrappers: { unmount(): void }[] = []
afterEach(() => wrappers.splice(0).forEach(wrapper => wrapper.unmount()))

describe('EUI charts', () => {
  it('keeps missing line points separate from zero and exposes formatted data', () => {
    const wrapper = mount(ELineChart, {
      props: {
        label: '访问趋势',
        categories: ['周一', '周二', '周三'],
        series: [{ key: 'web', label: '站点', values: [0, null, 12] }],
        formatValue: value => value + ' 次',
      },
    })
    wrappers.push(wrapper)

    expect(wrapper.get('figure').attributes('aria-label')).toBe('访问趋势')
    expect(wrapper.findAll('tbody tr').map(row => row.get('td').text())).toEqual(['0 次', '—', '12 次'])
    expect(wrapper.get('details summary').text()).toBe('查看数据')
  })

  it('uses the loading state before empty and preserves valid zero bars', async () => {
    const wrapper = mount(EBarChart, {
      props: { label: '处理量', categories: ['周一'], series: [], loading: true, height: 180 },
    })
    wrappers.push(wrapper)
    expect(wrapper.get('[role="status"]').text()).toContain('加载中')
    expect(wrapper.get('[data-slot="chart-plot"]').attributes('style')).toContain('180px')
    await wrapper.setProps({ loading: false })
    expect(wrapper.text()).toContain('暂无数据')
    await wrapper.setProps({ series: [{ key: 'count', label: '工单', values: [0] }] })
    expect(wrapper.get('tbody td').text()).toBe('0')
  })

  it('shows no ring for zero total and presents valid shares when data arrives', async () => {
    const wrapper = mount(EDonutChart, {
      props: {
        label: '来源占比',
        items: [{ key: 'direct', label: '直接', value: 0 }],
      },
    })
    wrappers.push(wrapper)
    expect(wrapper.find('table').exists()).toBe(false)
    await wrapper.setProps({ items: [{ key: 'direct', label: '直接', value: 3 }, { key: 'external', label: '外部', value: 1 }] })
    expect(wrapper.text()).toContain('75%')
    expect(wrapper.findAll('tbody td').map(cell => cell.text())).toEqual(['3', '75%', '1', '25%'])
  })

  it('retains a series color when the consumer changes its order', async () => {
    const web = { key: 'web', label: '站点', values: [1] }
    const app = { key: 'app', label: '应用', values: [2] }
    const wrapper = mount(ELineChart, {
      props: { label: '访问量', categories: ['周一'], series: [web, app] },
    })
    wrappers.push(wrapper)
    const swatches = () => wrapper.findAll('li span').map(span => span.attributes('style'))
    const before = swatches()
    expect(before[0]).toContain('--chart-1')
    expect(before[1]).toContain('--chart-2')
    await wrapper.setProps({ series: [app, web] })
    expect(swatches()).toEqual([...before].reverse())
  })
})
