/**
 * EChartContainer 图表容器组件的类型定义
 */

/**
 * 图表数据系列配置映射
 * key 为系列标识，value 包含其显示名称和主题色
 */
export type ChartConfig = {
  [k in string]: {
    /** 图例/tooltip 中显示的标签 */
    label?: string
    /** 系列颜色，会注入为 CSS 变量 --color-{key} 供子组件消费 */
    color?: string
  }
}

/**
 * EChartContainer 图表容器 Props
 */
export interface EChartContainerProps {
  /** 自定义 class，透传到容器 */
  class?: string
  /** 图表系列配置 */
  config: ChartConfig
  /** 图表唯一 id，缺省时自动生成随机 id */
  id?: string
}
