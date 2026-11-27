/** 常用图表共享的展示设置，业务数据由调用方准备。 */
export interface EChartProps {
  /** 辅助技术读取的图表名称。 */
  label: string
  /** 绘图区高度，单位为 px，宽度随容器变化。 */
  height?: number
  /** 数据请求期间使用加载状态。 */
  loading?: boolean
  /** 调整坐标轴、提示和数据表中的值。 */
  formatValue?: (value: number) => string
}

/** 与 categories 逐项对应的图表数据系列。 */
export interface EChartSeries {
  /** 系列的稳定标识，用于匹配图形与颜色。 */
  key: string
  /** 显示在图例、提示和数据表。 */
  label: string
  /** null 表示缺失点，0 表示有效数值。 */
  values: readonly (number | null)[]
}

/** 折线与柱状图使用同一轴和系列约定。 */
export interface ECartesianChartProps extends EChartProps {
  /** 从左到右的轴标签。 */
  categories: readonly string[]
  /** 按图例顺序传入。每组值与 categories 一一对应。 */
  series: readonly EChartSeries[]
}

/** 环图切片。比例由图表按全部有效非负数计算。 */
export interface EDonutChartItem {
  /** 数据项的稳定标识，用于匹配图形与颜色。 */
  key: string
  /** 显示在图例和数据表。 */
  label: string
  /** 有限的非负数。 */
  value: number
}

/** 单序列环图，用于展示组成比例。 */
export interface EDonutChartProps extends EChartProps {
  /** 按图例顺序传入。总和为 0 时显示空态。 */
  items: readonly EDonutChartItem[]
}
