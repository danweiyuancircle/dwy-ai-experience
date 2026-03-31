export type ChartConfig = {
  [k in string]: {
    label?: string
    color?: string
  }
}

export interface EChartContainerProps {
  class?: string
  config: ChartConfig
  id?: string
}
