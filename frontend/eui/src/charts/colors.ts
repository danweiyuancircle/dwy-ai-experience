import { computed } from 'vue'

const palette = ['var(--chart-1)', 'var(--chart-2)', 'var(--chart-3)', 'var(--chart-4)', 'var(--chart-5)']

/** 已显示的系列在重排时保留原色，新增系列使用下一个色位。 */
export function useChartColors(entries: () => readonly { key: string }[]) {
  return computed<Map<string, string>>((previous) => {
    const current = entries()
    const assigned = new Map<string, string>()
    for (const { key } of current) {
      const color = previous?.get(key)
      if (color) assigned.set(key, color)
    }
    for (const { key } of current) {
      if (assigned.has(key)) continue
      const used = [...assigned.values()]
      assigned.set(key, palette.find(color => !used.includes(color)) ?? palette[assigned.size % palette.length])
    }
    return assigned
  })
}
